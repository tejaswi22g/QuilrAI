
from fastapi import HTTPException, status


# Development-only mock credentials.
# Production systems should validate signed JWTs
# or use an identity provider.

TOKEN_ROLES = {
    "admin-secret": "admin",
    "viewer-secret": "viewer",
}


def authenticate_user(authorization: str | None) -> str:
    """
    Validate the Bearer token and return the user's role.
    """

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format",
        )

    token = parts[1]

    role = TOKEN_ROLES.get(token)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return role
