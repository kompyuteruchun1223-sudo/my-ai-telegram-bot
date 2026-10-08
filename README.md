# AI Telegram Bot

OpenAI API orqali ishlaydigan, SQLite xotirali, async Python Telegram AI bot.

Bot foydalanuvchi bilan tabiiy suhbat qiladi, oldingi suhbatning oxirgi xabarlarini kontekst sifatida
ishlatadi, foydalanuvchi tiliga moslashadi va personality orqali hazilkash, biroz g‘ururli,
samimiy uslubni saqlaydi.

## 1. Loyiha qanday ishlaydi?

Arxitektura:

Telegram user
    ↓
Telegram Bot API
    ↓
python-telegram-bot
    ↓
SQLite'dan user history
    ↓
Personality/system instructions
    ↓
OpenAI Responses API
    ↓
AI javobi
    ↓
SQLite'ga saqlash
    ↓
Telegram user

Har bir Telegram user uchun `user_id` bo‘yicha alohida history saqlanadi.

## 2. Fayllar

- `bot.py` — Telegram handlerlari, rate limit, typing action, admin komandalar va application.
- `config.py` — `.env` konfiguratsiyasini o‘qish va tekshirish.
- `ai.py` — OpenAI Async client va Responses API chaqiruvi.
- `database.py` — SQLite user va message history.
- `personality.py` — botning xarakteri va xavfsizlik qoidalari.
- `requirements.txt` — Python kutubxonalari.
- `.env.example` — kerakli environment variable namunasi.
- `.gitignore` — `.env`, SQLite va Python vaqtinchalik fayllarini Git'dan chiqaradi.
- `README.md` — o‘rnatish va sozlash qo‘llanmasi.

## 3. Talablar

Tavsiya:

- Python 3.11+
- Telegram akkaunt
- BotFather orqali yaratilgan Telegram bot
- OpenAI API key
- Internet

`python-telegram-bot` 22.8 Python 3.10+ talab qiladi. Python 3.11 bu loyiha uchun mos.

## 4. Windows'da Python o‘rnatish

1. Python 3.11 yoki undan yangi versiyani o‘rnating.
2. O‘rnatish vaqtida `Add Python to PATH` belgisini yoqing.
3. CMD yoki PowerShell oching:

```powershell
python --version
```

Agar Windows'da `python` ishlamasa:

```powershell
py --version
```

## 5. Loyihani yaratish

Masalan:

```powershell
mkdir ai_telegram_bot
cd ai_telegram_bot
```

Yuqoridagi barcha fayllarni shu papkaga joylashtiring.

## 6. Virtual environment

Windows:

```powershell
python -m venv .venv
```

Aktivlashtirish:

```powershell
.venv\Scripts\activate
```

Agar `python` o‘rniga `py` ishlatsangiz:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

Terminal boshida `(.venv)` ko‘rinsa, virtual environment aktiv.

## 7. Kutubxonalarni o‘rnatish

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 8. Telegram Bot yaratish

Telegram'da `@BotFather` ni oching.

1. `/newbot` yuboring.
2. Bot nomini kiriting.
3. Username kiriting.
4. BotFather bergan tokenni saqlang.

Tokenni hech kimga yubormang va GitHub'ga joylamang.

## 9. Telegram tokenni olish

BotFather bergan qiymat:

```text
123456789:AAxxxxxxxxxxxxxxxxxxxxxxxx
```

Bu qiymat `.env` ichidagi:

```env
TELEGRAM_BOT_TOKEN=...
```

ga yoziladi.

## 10. OpenAI API key

OpenAI platformasidan API key yarating.

`.env`:

```env
OPENAI_API_KEY=your_openai_api_key
```

API keyni Python kodiga yozmang.

## 11. `.env` yaratish

`.env.example` faylidan nusxa olib `.env` nomi bilan saqlang.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Keyin `.env` ni ochib qiymatlarni kiriting.

Misol:

```env
TELEGRAM_BOT_TOKEN=123456789:AA...
OPENAI_API_KEY=sk-...
ADMIN_ID=123456789
OPENAI_MODEL=gpt-6-luna
DATABASE_PATH=bot.db
MAX_HISTORY=20
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=30
MAX_USER_MESSAGE_CHARS=8000
LOG_LEVEL=INFO
```

`.env` Git'ga ketmasligi uchun `.gitignore` ichida bor.

## 12. ADMIN_ID ni qanday olish?

Telegram'dagi shaxsiy numeric user ID'ingiz kerak.

Buni Telegram'dagi ishonchli user-ID botlari yoki o‘zingizga tegishli Telegram integratsiyasi orqali
aniqlashingiz mumkin.

`.env`:

```env
ADMIN_ID=123456789
```

`/stats` faqat shu ID uchun ishlaydi.

## 13. Botni ishga tushirish

Virtual environment aktiv bo‘lgandan keyin:

```powershell
python bot.py
```

Konsolda:

```text
Starting Telegram bot...
Bot initialized successfully.
```

ga o‘xshash log ko‘rsangiz, bot ishlayapti.

Telegram'da botga:

```text
/start
```

yuboring.

Keyin oddiy xabar yuboring.

## 14. Komandalar

### `/start`

Suhbatni boshlaydi.

### `/help`

Botdan foydalanish bo‘yicha yordam beradi.

### `/clear`

Shu foydalanuvchining SQLite'dagi suhbat tarixini o‘chiradi.

### `/about`

Bot haqida qisqa ma'lumot.

### `/stats`

Faqat `ADMIN_ID` uchun:

- jami foydalanuvchilar
- bugungi foydalanuvchilar
- jami xabarlar

ko‘rsatiladi.

## 15. Personality qayerda?

`personality.py`

Asosiy system prompt:

```python
get_system_prompt(user)
```

shu funksiyada joylashgan.

Botning:
- hazili
- g‘ururi
- til qoidalari
- jiddiy suhbatdagi xatti-harakati
- xavfsizlik qoidalari
- system promptni himoya qilish

shu faylda boshqariladi.

Personalityni o‘zgartirgandan keyin botni qayta ishga tushiring.

## 16. AI modelini o‘zgartirish

Model `.env` orqali boshqariladi:

```env
OPENAI_MODEL=gpt-6-luna
```

Boshqa modeldan foydalanmoqchi bo‘lsangiz, OpenAI API account'ingiz uchun mavjud model ID'sini yozing.

Kodning o‘zini o‘zgartirish shart emas.

## 17. MAX_HISTORY

`.env`:

```env
MAX_HISTORY=20
```

Bu OpenAI'ga har bir yangi xabar bilan yuboriladigan oxirgi suhbat xabarlari soni.

Masalan:

```text
MAX_HISTORY=10
```

kamroq kontekst va odatda kamroq input token.

```text
MAX_HISTORY=30
```

ko‘proq kontekst, lekin API xarajati oshishi mumkin.

## 18. SQLite qayerda?

`.env`:

```env
DATABASE_PATH=bot.db
```

bo‘lsa, `bot.db` loyiha papkasida yaratiladi.

Database ichida:

### users

- user_id
- first_name
- last_name
- username
- created_at
- last_seen_at

### messages

- id
- user_id
- role
- message
- timestamp

saqlanadi.

`user_id` orqali foydalanuvchilar bir-biridan ajratiladi.

## 19. API xarajatlarini kamaytirish

Eng muhim sozlama:

```env
MAX_HISTORY=20
```

Uni 10-15 ga tushirish mumkin.

Yana:

```env
MAX_USER_MESSAGE_CHARS=8000
```

orqali juda uzun xabarlarni cheklash mumkin.

Rate limit:

```env
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=30
```

Bu bitta user uchun 30 soniyada 5 ta request bilan cheklaydi.

Real loyihada global budget/usage monitoring ham qo‘shish tavsiya qilinadi.

## 20. Rate limit qanday ishlaydi?

Default:

```text
5 request / 30 seconds / user
```

Limit oshsa:

```text
Sekinroq 😅 Miyamga navbat bilan murojaat qilaylik...
```

degan xabar chiqadi.

Bu botning oddiy application-level rate limiteridir.

## 21. Typing effect

AI javob tayyorlayotganda bot Telegram'ga:

```text
typing...
```

action yuboradi.

Bu `bot.py` ichidagi `typing_loop()` orqali ishlaydi.

## 22. Xatolar

Foydalanuvchiga OpenAI exception, API key yoki texnik stack trace yuborilmaydi.

Masalan OpenAI API ishlamasa:

```text
Bir daqiqa, miyamga internet yetib bormay qoldi 😅 Keyinroq yana yozib ko‘r.
```

ko‘rsatiladi.

Texnik xato esa server/console log'iga yoziladi.

## 23. 24/7 ishlatish

Windows kompyuterda `python bot.py` faqat kompyuter va terminal ishlayotgan vaqt davomida botni
ishlatadi.

Haqiqiy 24/7 uchun VPS tavsiya qilinadi.

Misol:

- Ubuntu VPS
- 1 GB RAM odatda bunday yengil bot uchun boshlang‘ich darajada yetarli bo‘lishi mumkin
- Python 3.11+
- systemd

## 24. Ubuntu VPS

SSH orqali serverga kiring:

```bash
ssh root@YOUR_SERVER_IP
```

Python:

```bash
apt update
apt install -y python3 python3-venv python3-pip
```

Loyiha:

```bash
mkdir -p /opt/ai_telegram_bot
cd /opt/ai_telegram_bot
```

Fayllarni serverga joylang.

Virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Kutubxonalar:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

`.env` ni serverga joylang:

```bash
nano .env
```

Token va API keyni kiriting.

## 25. VPS'da qo‘lda test

```bash
source .venv/bin/activate
python bot.py
```

Telegram'dan botga xabar yuborib tekshiring.

Agar ishlasa `Ctrl+C` bilan to‘xtating.

## 26. systemd bilan 24/7

Service:

```bash
nano /etc/systemd/system/ai-telegram-bot.service
```

Ichiga:

```ini
[Unit]
Description=AI Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai_telegram_bot
EnvironmentFile=/opt/ai_telegram_bot/.env
ExecStart=/opt/ai_telegram_bot/.venv/bin/python /opt/ai_telegram_bot/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Keyin:

```bash
systemctl daemon-reload
systemctl enable ai-telegram-bot
systemctl start ai-telegram-bot
```

Status:

```bash
systemctl status ai-telegram-bot
```

Log:

```bash
journalctl -u ai-telegram-bot -f
```

To‘xtatish:

```bash
systemctl stop ai-telegram-bot
```

Qayta ishga tushirish:

```bash
systemctl restart ai-telegram-bot
```

## 27. VPS'da yangilash

Kod yangilangandan keyin:

```bash
cd /opt/ai_telegram_bot
source .venv/bin/activate
pip install -r requirements.txt
systemctl restart ai-telegram-bot
```

## 28. Xavfsizlik

Hech qachon:

```python
OPENAI_API_KEY = "sk-..."
```

yoki:

```python
TELEGRAM_BOT_TOKEN = "123:..."
```

kabi hardcode qilmang.

`.env` ni GitHub'ga push qilmang.

Agar token oshkor bo‘lsa:
- Telegram bot tokenini BotFather orqali yangilang.
- OpenAI API keyni bekor qiling va yangisini yarating.

## 29. Git bilan ishlash

```bash
git init
git add .
git commit -m "Initial AI Telegram bot"
```

`.gitignore` sababli `.env` va `bot.db` Git'ga qo‘shilmaydi.

## 30. Keyinchalik qo‘shish mumkin bo‘lgan funksiyalar

Loyihani keyinchalik quyidagilar bilan kengaytirish mumkin:

- uzoq muddatli user memory
- avtomatik conversation summary
- ovozli xabarni matnga aylantirish
- AI voice reply
- rasm tahlili
- admin broadcast
- foydalanuvchi bloklash
- premium users
- usage/token statistikasi
- Redis rate limit
- PostgreSQL
- Docker
- webhook
- monitoring
- health check
- analytics

## 31. Muhim eslatma

Bu loyiha OpenAI API uchun alohida API billing talab qilishi mumkin. ChatGPT Plus obunasi
OpenAI API foydalanishini avtomatik ravishda bepul qilmaydi.

API model va narxlar OpenAI platformasidagi amaldagi tarifga bog‘liq.

## 32. Tezkor tekshiruv

Agar bot ishlamasa:

1. Python:
```bash
python --version
```

2. Paketlar:
```bash
pip install -r requirements.txt
```

3. `.env` mavjudmi?

Windows:
```powershell
dir -Force
```

4. Token borligini tekshiring.

5. OpenAI API key borligini tekshiring.

6. `bot.py` ishga tushiring:
```bash
python bot.py
```

7. Console'dagi errorni tekshiring.

8. Telegram botga `/start` yuboring.

9. Oddiy matn yuboring.

## 33. Production uchun tavsiya

Boshlanishida SQLite yetarli.

Foydalanuvchilar va xabarlar soni sezilarli oshsa PostgreSQL + Redis'ga o'tish ma'qul.

Rate limit hozircha process memory'da ishlaydi. Bir nechta server instance ishlatilsa Redis kabi
markazlashgan rate limiter kerak bo‘ladi.
