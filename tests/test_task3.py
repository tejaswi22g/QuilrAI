import pytest
from task3_llm_guardrail.guardrail import PIIRedactor


def test_email_redaction():
    redactor = PIIRedactor()
    result = redactor.feed("Contact john@example.com", final=True)
    assert "john@example.com" not in result
    assert "[REDACTED]" in result


def test_ssn_redaction():
    redactor = PIIRedactor()
    result = redactor.feed("SSN: 123-45-6789", final=True)
    assert "123-45-6789" not in result
    assert "[REDACTED]" in result


def test_credit_card_redaction():
    redactor = PIIRedactor()
    result = redactor.feed("Card: 4111 1111 1111 1111", final=True)
    assert "4111 1111 1111 1111" not in result
    assert "[REDACTED]" in result


def test_email_split_across_chunks():
    redactor = PIIRedactor()
    first = redactor.feed("Contact john.smi")
    second = redactor.feed("th@example.com", final=True)

    result = first + second

    assert "john.smith@example.com" not in result
    assert "[REDACTED]" in result


def test_ssn_split_across_chunks():
    redactor = PIIRedactor()
    first = redactor.feed("SSN: 123-")
    second = redactor.feed("45-6789", final=True)

    result = first + second

    assert "123-45-6789" not in result
    assert "[REDACTED]" in result

def test_valid_credit_card_passes_luhn():
    redactor = PIIRedactor()
    result = redactor.feed("Card: 4111 1111 1111 1111", final=True)

    assert "4111 1111 1111 1111" not in result
    assert "[REDACTED]" in result


def test_invalid_credit_card_checksum_not_redacted():
    redactor = PIIRedactor()
    result = redactor.feed("Card: 4111 1111 1111 1112", final=True)

    assert "4111 1111 1111 1112" in result


def test_pii_redaction_after_long_stream():
    redactor = PIIRedactor()

    first = redactor.feed("A" * 600)
    second = redactor.feed(" Contact: john@example.com", final=True)

    result = first + second

    assert "john@example.com" not in result
    assert "[REDACTED]" in result