import pytest
from pydantic import ValidationError

from task1_mcp_server.server import (
    CustomerRequest,
    RefundRequest,
)


def test_valid_customer_id():
    request = CustomerRequest(
        customer_id="CUST-12345"
    )
    assert request.customer_id == "CUST-12345"


def test_invalid_customer_id():
    with pytest.raises(ValidationError):
        CustomerRequest(customer_id="ABC-12345")


def test_valid_refund():
    request = RefundRequest(
        customer_id="CUST-12345",
        amount=100.0,
        reason="Duplicate payment",
    )
    assert request.amount == 100.0


def test_negative_refund():
    with pytest.raises(ValidationError):
        RefundRequest(
            customer_id="CUST-12345",
            amount=-100.0,
            reason="Duplicate payment",
        )


def test_zero_refund():
    with pytest.raises(ValidationError):
        RefundRequest(
            customer_id="CUST-12345",
            amount=0.0,
            reason="Duplicate payment",
        )


def test_short_reason():
    with pytest.raises(ValidationError):
        RefundRequest(
            customer_id="CUST-12345",
            amount=100.0,
            reason="Refund",
        )


def test_string_amount():
    with pytest.raises(ValidationError):
        RefundRequest(
            customer_id="CUST-12345",
            amount="100",
            reason="Duplicate payment",
        )


def test_unexpected_field():
    with pytest.raises(ValidationError):
        RefundRequest(
            customer_id="CUST-12345",
            amount=100.0,
            reason="Duplicate payment",
            admin=True,
        )