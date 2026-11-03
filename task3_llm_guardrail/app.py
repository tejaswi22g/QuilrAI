from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from task3_llm_guardrail.guardrail import PIIRedactor
from task3_llm_guardrail.mock_provider import stream_mock_response

app = FastAPI(title="QuilrAI LLM PII Guardrail")


async def guarded_stream():
    redactor = PIIRedactor()

    async for chunk in stream_mock_response():
        safe_chunk = redactor.feed(chunk)

        if safe_chunk:
            yield safe_chunk

    # Flush the remaining buffered text after redaction.
    final_chunk = redactor.feed("", final=True)

    if final_chunk:
        yield final_chunk


@app.get("/stream")
async def stream_response():
    return StreamingResponse(
        guarded_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )