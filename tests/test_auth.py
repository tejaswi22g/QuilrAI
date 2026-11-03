import pytest
from fastapi import HTTPException

from task2_mcp_gateway.auth import authenticate_user


def test_admin_authentication():
    assert authenticate_user("Bearer admin-secret") == "admin"


def test_viewer_authentication():
    assert authenticate_user("Bearer viewer-secret") == "viewer"


def test_missing_token():
    with pytest.raises(HTTPException) as exc:
        authenticate_user(None)

    assert exc.value.status_code == 401


def test_invalid_token():
    with pytest.raises(HTTPException) as exc:
        authenticate_user("Bearer wrong-token")

    assert exc.value.status_code == 401


def test_invalid_scheme():
    with pytest.raises(HTTPException):
        authenticate_user("Basic admin-secret")