
import asyncio
import json
import logging
import sys

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# --------------------------------------------------
# 1. Logging configuration
# --------------------------------------------------

# stdout is reserved for MCP JSON-RPC messages.
# All application logs must go to stderr.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger("quilrai-mcp-server")


# --------------------------------------------------
# 2. Strict Pydantic input schemas
# --------------------------------------------------

class StrictRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )


class CustomerRequest(StrictRequest):
    customer_id: str = Field(
        pattern=r"^CUST-[0-9]{5}$",
        description="Customer ID in CUST-XXXXX format",
    )


class RefundRequest(CustomerRequest):
    amount: float = Field(
        gt=0,
        allow_inf_nan=False,
        description="Refund amount must be positive",
    )

    reason: str = Field(
        min_length=10,
        description="Refund reason must contain at least 10 characters",
    )


# --------------------------------------------------
# 3. Mock customer database
# --------------------------------------------------

CUSTOMERS = {
    "CUST-12345": {
        "customer_id": "CUST-12345",
        "name": "John Smith",
        "email": "john@example.com",
        "account_status": "active",
        "balance": 500.00,
    },
    "CUST-67890": {
        "customer_id": "CUST-67890",
        "name": "Sarah Johnson",
        "email": "sarah@example.com",
        "account_status": "active",
        "balance": 750.00,
    },
}


# --------------------------------------------------
# 4. Initialize low-level MCP server
# --------------------------------------------------

server = Server("quilrai-customer-server")


# --------------------------------------------------
# 5. Register available MCP tools
# --------------------------------------------------

@server.list_tools()
async def list_tools() -> list[Tool]:

    return [
        Tool(
            name="get_customer_record",
            description="Retrieve customer information using customer ID.",
            inputSchema=CustomerRequest.model_json_schema(),
        ),
        Tool(
            name="trigger_refund",
            description="Validate and simulate a customer refund.",
            inputSchema=RefundRequest.model_json_schema(),
        ),
    ]


# --------------------------------------------------
# 6. Handle MCP tool execution
# --------------------------------------------------

@server.call_tool()
async def call_tool(
    name: str,
    arguments: dict[str, Any],
) -> list[TextContent]:

    try:

        # ------------------------------------------
        # Customer lookup
        # ------------------------------------------

        if name == "get_customer_record":

            request = CustomerRequest.model_validate(
                arguments,
                strict=True,
            )

            logger.info(
                "Customer lookup requested: %s",
                request.customer_id,
            )

            customer = CUSTOMERS.get(request.customer_id)

            if customer is None:
                raise ValueError("Customer record not found")

            return [
                TextContent(
                    type="text",
                    text=json.dumps(customer),
                )
            ]

        # ------------------------------------------
        # Refund processing
        # ------------------------------------------

        elif name == "trigger_refund":

            request = RefundRequest.model_validate(
                arguments,
                strict=True,
            )

            if request.customer_id not in CUSTOMERS:
                raise ValueError("Customer record not found")

            logger.info(
                "Refund requested for customer: %s",
                request.customer_id,
            )

            refund_result = {
                "status": "success",
                "message": "Refund request accepted",
                "customer_id": request.customer_id,
                "amount": request.amount,
                "reason": request.reason,
            }

            logger.info(
                "Refund validation successful: %.2f",
                request.amount,
            )

            return [
                TextContent(
                    type="text",
                    text=json.dumps(refund_result),
                )
            ]

        else:
            raise ValueError("Unknown tool requested")

    except ValidationError as exc:

        # Do not expose internal implementation details.
        # Return a clean MCP tool error.

        error_details = [
            {
                "field": ".".join(str(part) for part in error["loc"]),
                "message": error["msg"],
            }
            for error in exc.errors()
        ]

        logger.warning("Tool input validation failed")

        raise ValueError(
            "Invalid tool arguments: " +
            json.dumps(error_details)
        ) from None

    except ValueError as exc:

        logger.warning("Tool execution rejected: %s", exc)

        raise


# --------------------------------------------------
# 7. Start MCP server using STDIO
# --------------------------------------------------

async def main():

    logger.info("Starting QuilrAI MCP customer server")

    async with stdio_server() as (read_stream, write_stream):

        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
