from fastapi import Request

from app.core.trino import TrinoClient


def get_trino_client(request: Request) -> TrinoClient:
    return request.app.state.trino
