import os

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from task2_mcp_gateway.auth import authenticate_user

app = FastAPI(title="QuilrAI MCP Security Gateway")

DOWNSTREAM_URL = os.getenv(
    "MCP_DOWNSTREAM_URL",
    "http://127.0.0.1:8001/mcp",
)


@app.post("/mcp")
async def proxy_mcp(
    payload: dict,
    authorization: str | None = Header(default=None),
):
    # Step 1: Authenticate the caller
    role = authenticate_user(authorization)

    # Step 2: Inspect the JSON-RPC method
    method = payload.get("method")

    # Step 3: Apply authorization to tool calls
    if method == "tools/call":
        tool_name = payload.get("params", {}).get("name", "")

        if tool_name.startswith("admin_") and role != "admin":
            return JSONResponse(
                status_code=200,
                content={
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "error": {
                        "code": -32001,
                        "message": "Unauthorized Tool Call",
                    },
                },
            )

    # Step 4: Forward authorized requests to downstream MCP server
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                DOWNSTREAM_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Downstream MCP server unavailable",
        )