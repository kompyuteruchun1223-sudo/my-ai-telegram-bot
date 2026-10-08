import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone

from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ai import generate_reply
from config import settings
from database import Database
from personality import get_system_prompt

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
)
logger = logging.getLogger(__name__)

db = Database(settings.database_path)

user_locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
rate_buckets: dict[int, deque[float]] = defaultdict(deque)


def is_rate_limited(user_id: int) -> bool:
    now = datetime.now(timezone.utc).timestamp()
    bucket = rate_buckets[user_id]

    while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
        bucket.popleft()

    if len(bucket) >= settings.rate_limit_requests:
        return True

    bucket.append(now)
    return False


def split_message(text: str, limit: int = 4096) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text

    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at < limit // 2:
            split_at = limit

        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()

    if remaining:
        chunks.append(remaining)

    return chunks


async def typing_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, stop_event: asyncio.Event):
    try:
        while not stop_event.is_set():
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=4.0)
            except asyncio.TimeoutError:
                pass
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.debug("Typing action failed for chat_id=%s", chat_id, exc_info=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    await db.upsert_user(
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
    )

    await update.message.reply_text(
        "Salom 😏 Men shu yerdaman. Gaplashamizmi? "
        "Xohlasang savol ber, xohlasang shunchaki suhbatlashamiz."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "/start — suhbatni boshlash\n"
        "/help — yordam\n"
        "/clear — suhbat tarixini tozalash\n"
        "/about — bot haqida\n\n"
        "Oddiygina xabar yozishing ham yetarli. Men javob beraman 😎"
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    await db.clear_history(update.effective_user.id)
    await update.message.reply_text(
        "Bo‘ldi. Eski suhbat tarixini tozaladim 🧹\n"
        "Endi toza sahifadan boshlaymiz."
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Men OpenAI API orqali ishlaydigan AI Telegram botman. "
        "Suhbat kontekstini SQLite'da foydalanuvchi ID bo‘yicha alohida saqlayman. "
        "Xarakterim esa biroz hazilkash, biroz g‘ururli 😏"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    if settings.admin_id is None or update.effective_user.id != settings.admin_id:
        await update.message.reply_text("Bu komandaga ruxsating yo‘q 🙂")
        return

    stats = await db.get_stats()

    await update.message.reply_text(
        "📊 Bot statistikasi\n\n"
        f"Jami foydalanuvchilar: {stats['total_users']}\n"
        f"Bugungi foydalanuvchilar: {stats['today_users']}\n"
        f"Jami xabarlar: {stats['total_messages']}"
    )


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message or not update.message.text:
        return

    user = update.effective_user
    user_id = user.id
    user_text = update.message.text.strip()

    if not user_text:
        return

    if len(user_text) > settings.max_user_message_chars:
        await update.message.reply_text(
            f"Xabar juda uzun. Iltimos, {settings.max_user_message_chars:,} "
            "belgidan qisqaroq qilib yubor."
        )
        return

    await db.upsert_user(
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
    )

    if is_rate_limited(user_id):
        await update.message.reply_text(
            "Sekinroq 😅 Miyamga navbat bilan murojaat qilaylik. "
            "Bir necha soniyadan keyin yana yoz."
        )
        return

    async with user_locks[user_id]:
        history = await db.get_history(user_id, settings.max_history)
        system_prompt = get_system_prompt(user)

        stop_typing = asyncio.Event()
        typing_task = asyncio.create_task(
            typing_loop(context, update.effective_chat.id, stop_typing)
        )

        try:
            reply = await generate_reply(
                system_prompt=system_prompt,
                history=history,
                user_message=user_text,
            )

            if not reply:
                raise RuntimeError("OpenAI returned an empty response.")

            await db.add_message(user_id, "user", user_text)
            await db.add_message(user_id, "assistant", reply)

            for chunk in split_message(reply):
                await update.message.reply_text(chunk)

        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as exc:
            logger.exception("OpenAI API error for user_id=%s: %s", user_id, exc)
            await update.message.reply_text(
                "Bir daqiqa, miyamga internet yetib bormay qoldi 😅 "
                "Keyinroq yana yozib ko‘r."
            )
        except Exception as exc:
            logger.exception("Unexpected error for user_id=%s: %s", user_id, exc)
            await update.message.reply_text(
                "Hozir bir joyim qotib qoldi 😅 Keyinroq yana urinib ko‘r."
            )
        finally:
            stop_typing.set()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception(
        "Unhandled Telegram error",
        exc_info=context.error,
    )


async def post_init(application: Application) -> None:
    await db.initialize()

    await application.bot.set_my_commands(
        [
            ("start", "Suhbatni boshlash"),
            ("help", "Yordam"),
            ("clear", "Suhbat tarixini tozalash"),
            ("about", "Bot haqida"),
            ("stats", "Admin statistikasi"),
        ]
    )

    logger.info("Bot initialized successfully.")


async def post_shutdown(application: Application) -> None:
    await db.close()
    logger.info("Database closed.")


def build_application() -> Application:
    application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler)
    )
    application.add_error_handler(error_handler)

    return application


def main() -> None:
    application = build_application()
    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
