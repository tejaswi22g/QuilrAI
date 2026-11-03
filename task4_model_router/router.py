import asyncio
import httpx

from task4_model_router.mock_providers import (
    primary_model,
    secondary_model,
)


PRIMARY_TIMEOUT_SECONDS = 3.0


async def route_request(prompt: str, primary_behavior: str = "success") -> dict:
    try:
        result = await asyncio.wait_for(
            primary_model(prompt, primary_behavior),
            timeout=PRIMARY_TIMEOUT_SECONDS,
        )

        return {
            "status": "success",
            "fallback_used": False,
            "data": result,
        }

    except asyncio.TimeoutError:
        # Primary model exceeded the 3-second timeout.
        fallback_reason = "primary_timeout"

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 429:
            return {
                "status": "error",
                "fallback_used": False,
                "error": "Primary model request failed",
            }

        fallback_reason = "primary_rate_limited"

    try:
        fallback_result = await secondary_model(prompt)

        return {
            "status": "success",
            "fallback_used": True,
            "fallback_reason": fallback_reason,
            "data": fallback_result,
        }

    except Exception:
        return {
            "status": "error",
            "fallback_used": True,
            "error": "All model providers are unavailable",
        }