import asyncio
import httpx


async def primary_model(prompt: str, behavior: str = "success") -> dict:
    if behavior == "rate_limit":
        raise httpx.HTTPStatusError(
            "Primary model rate limited",
            request=httpx.Request("POST", "http://primary-model"),
            response=httpx.Response(429),
        )

    if behavior == "timeout":
        await asyncio.sleep(5)

    if behavior != "success" and behavior not in ("rate_limit", "timeout"):
        raise ValueError("Unknown primary model behavior")

    return {
        "model": "primary-model",
        "response": f"Primary model processed: {prompt}",
    }


async def secondary_model(prompt: str) -> dict:
    await asyncio.sleep(0.1)

    return {
        "model": "secondary-model",
        "response": f"Secondary model processed: {prompt}",
    }