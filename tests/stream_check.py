import asyncio
import time
import httpx


async def main():
    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream(
            "GET",
            "http://127.0.0.1:8002/stream",
        ) as response:

            print("HTTP status:", response.status_code)

            async for chunk in response.aiter_text():
                elapsed = time.perf_counter() - start
                print(f"[{elapsed:.2f}s] Received: {chunk[:100]}")


asyncio.run(main())