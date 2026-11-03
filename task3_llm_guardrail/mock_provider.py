import asyncio


async def stream_mock_response():
    chunks = [
        "Hello! " * 60,
        "Your contact email is john.smi",
        "th@example.com. ",
        "Your SSN is 123-",
        "45-6789. ",
        "Your card number is 4111 1111 ",
        "1111 1111. ",
        "Thank you!",
    ]

    for chunk in chunks:
        await asyncio.sleep(0.3)
        yield chunk