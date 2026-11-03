import httpx
import pytest


GATEWAY_URL = "http://127.0.0.1:8000"
MOCK_URL = "http://127.0.0.1:8001"


@pytest.mark.asyncio
async def test_viewer_can_list_tools():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GATEWAY_URL}/mcp",
            headers={"Authorization": "Bearer viewer-secret"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
            },
        )

    assert response.status_code == 200
    tools = response.json()["result"]["tools"]
    names = [tool["name"] for tool in tools]

    assert "get_customer_record" in names
    assert "admin_delete_customer" in names


@pytest.mark.asyncio
async def test_viewer_cannot_call_admin_tool():
    async with httpx.AsyncClient() as client:
        await client.post(f"{MOCK_URL}/calls/reset")

        response = await client.post(
            f"{GATEWAY_URL}/mcp",
            headers={"Authorization": "Bearer viewer-secret"},
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "admin_delete_customer",
                    "arguments": {},
                },
            },
        )

        calls_response = await client.get(f"{MOCK_URL}/calls")

    assert response.status_code == 200
    assert response.json()["error"]["code"] == -32001
    assert response.json()["error"]["message"] == "Unauthorized Tool Call"

    # Prove the blocked request never reached the downstream server.
    assert "admin_delete_customer" not in calls_response.json()["calls"]


@pytest.mark.asyncio
async def test_admin_can_call_admin_tool():
    async with httpx.AsyncClient() as client:
        await client.post(f"{MOCK_URL}/calls/reset")

        response = await client.post(
            f"{GATEWAY_URL}/mcp",
            headers={"Authorization": "Bearer admin-secret"},
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "admin_delete_customer",
                    "arguments": {},
                },
            },
        )

        calls_response = await client.get(f"{MOCK_URL}/calls")

    assert response.status_code == 200
    assert "result" in response.json()
    assert "admin_delete_customer" in calls_response.json()["calls"]