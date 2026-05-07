from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.security import verify_basic_credentials
from app.infrastructure.trino.client import TrinoClient

_http_basic = HTTPBasic()


def require_basic_auth(
    credentials: HTTPBasicCredentials = Depends(_http_basic),
) -> HTTPBasicCredentials:
    if not verify_basic_credentials(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


def get_trino_client(request: Request) -> TrinoClient:
    return request.app.state.trino
