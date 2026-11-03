from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from task4_model_router.database import (
    initialize_database,
    reserve_tokens,
)
from task4_model_router.router import route_request


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield


app = FastAPI(
    title="QuilrAI Model Router",
    lifespan=lifespan,
)


class ModelRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)
    estimated_tokens: int = Field(gt=0, le=50000)
    primary_behavior: str = Field(
        default="success",
        pattern="^(success|rate_limit|timeout)$",
    )


@app.post("/generate")
async def generate(
    request: ModelRequest,
    x_tenant_id: str = Header(default=""),
):
    if not x_tenant_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Tenant ID is required",
        )

    try:
        # Step 1: Reserve tokens before calling a model.
        usage = await reserve_tokens(
            x_tenant_id,
            request.estimated_tokens,
        )

        if not usage["allowed"]:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Token rate limit exceeded",
                    "limit": usage["limit"],
                    "current_usage": usage["current_usage"],
                    "remaining_tokens": usage["remaining_tokens"],
                },
            )

        # Step 2: Route to primary model or fallback.
        result = await route_request(
            request.prompt,
            request.primary_behavior,
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=503,
                detail=result["error"],
            )

        return {
            **result,
            "usage": usage,
        }

    except HTTPException:
        raise

    except Exception:
        # Don't expose internal stack traces or database details.
        raise HTTPException(
            status_code=500,
            detail="Internal model routing error",
        ) from None