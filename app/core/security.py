import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from graphql import GraphQLError
from strawberry.types import Info

from app.core.config import settings


def create_access_token(user_id: int, username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "username": username, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise GraphQLError("Invalid or expired token.") from exc


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    derived_b64 = base64.b64encode(derived).decode("ascii")
    return f"{salt_b64}${derived_b64}"


def verify_password(password: str, encoded_password: str) -> bool:
    try:
        salt_b64, stored_hash_b64 = encoded_password.split("$", maxsplit=1)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        stored_hash = base64.b64decode(stored_hash_b64.encode("ascii"))
    except ValueError:
        return False

    candidate_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(candidate_hash, stored_hash)


def get_auth_from_header(info: Info) -> dict:
    request = info.context.get("request")
    if request is None:
        raise GraphQLError("Request context not available.")

    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise GraphQLError("Unauthorized. Send Authorization: Bearer <token>.")

    token = auth_header.removeprefix("Bearer ").strip()
    return decode_access_token(token)
