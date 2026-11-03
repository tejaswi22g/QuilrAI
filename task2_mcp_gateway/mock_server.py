from fastapi import FastAPI

app = FastAPI(title="Mock Downstream MCP Server")

# Used to verify whether a request reached the downstream server.
CALL_LOG = []


@app.post("/mcp")
async def handle_mcp(payload: dict):
    method = payload.get("method")
    request_id = payload.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "get_customer_record",
                        "description": "Retrieve a customer record",
                        "inputSchema": {"type": "object"},
                    },
                    {
                        "name": "admin_delete_customer",
                        "description": "Delete a customer record",
                        "inputSchema": {"type": "object"},
                    },
                ]
            },
        }

    if method == "tools/call":
        params = payload.get("params", {})
        tool_name = params.get("name", "")

        CALL_LOG.append(tool_name)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Mock tool '{tool_name}' executed successfully",
                    }
                ]
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": "Method not found",
        },
    }
@app.get("/calls")
async def get_calls():
    return {"calls": CALL_LOG}


@app.post("/calls/reset")
async def reset_calls():
    CALL_LOG.clear()
    return {"message": "Call log cleared"}