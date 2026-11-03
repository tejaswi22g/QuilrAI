import pytest
import asyncio

from task4_model_router.database import (
    initialize_database,
    reserve_tokens,
)


@pytest.mark.asyncio
async def test_tokens_within_limit():
    await initialize_database()

    result = await reserve_tokens("tenant-test-1", 1000)

    assert result["allowed"] is True
    assert result["current_usage"] == 1000


@pytest.mark.asyncio
async def test_rejects_request_over_limit():
    await initialize_database()

    result = await reserve_tokens(
        "tenant-test-2",
        51000,
    )

    assert result["allowed"] is False


@pytest.mark.asyncio
async def test_tenant_isolation():
    await initialize_database()

    await reserve_tokens("tenant-test-3", 40000)

    result = await reserve_tokens("tenant-test-4", 20000)

    assert result["allowed"] is True


@pytest.mark.asyncio
async def test_rejects_invalid_token_count():
    await initialize_database()

    with pytest.raises(ValueError):
        await reserve_tokens("tenant-test-5", -100)


@pytest.mark.asyncio
async def test_rejects_zero_tokens():
    await initialize_database()

    with pytest.raises(ValueError):
        await reserve_tokens("tenant-test-6", 0)
        
@pytest.mark.asyncio
async def test_concurrent_requests_cannot_exceed_limit():
    await initialize_database()

    tenant_id = "tenant-concurrency-test"

    results = await asyncio.gather(
        *[
            reserve_tokens(tenant_id, 6000)
            for _ in range(10)
        ]
    )

    allowed = [r for r in results if r["allowed"]]
    rejected = [r for r in results if not r["allowed"]]

    assert len(allowed) == 8
    assert len(rejected) == 2

    assert sum(r["requested_tokens"] for r in allowed) == 48000