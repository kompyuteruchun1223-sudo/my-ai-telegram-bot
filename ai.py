from openai import AsyncOpenAI

from config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_reply(
    *,
    system_prompt: str,
    history: list[dict[str, str]],
    user_message: str,
) -> str:
    input_items: list[dict[str, str]] = []

    for item in history:
        input_items.append(
            {
                "role": item["role"],
                "content": item["message"],
            }
        )

    input_items.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    response = await client.responses.create(
        model=settings.openai_model,
        instructions=system_prompt,
        input=input_items,
    )

    return response.output_text.strip()
