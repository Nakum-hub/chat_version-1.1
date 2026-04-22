from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.errors import AppError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    expiration = now + (expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes))
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "typ": "access",
        "iat": int(now.timestamp()),
        "exp": int(expiration.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AppError(code="token_expired", message="The access token has expired.", status_code=401) from exc
    except jwt.InvalidTokenError as exc:
        raise AppError(code="invalid_token", message="The access token is invalid.", status_code=401) from exc
    if payload.get("typ") != "access":
        raise AppError(code="invalid_token", message="The access token is invalid.", status_code=401)
    return payload