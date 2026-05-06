from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from trino.auth import BasicAuthentication

from app.core.config import settings


class TrinoClient:
    """Fundação Trino do app — equivalente ao database.py do SQLAlchemy async.

    O dialeto SQLAlchemy Trino é síncrono. Queries rodam no ThreadPoolExecutor
    para não bloquear o event loop do FastAPI. O QueuePool do SQLAlchemy
    gerencia o reuso de conexões automaticamente.
    """

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=settings.TRINO_POOL_SIZE,
            thread_name_prefix="trino",
        )
        self._factory: sessionmaker[Session] = self._create_factory()

    @staticmethod
    def _create_factory() -> sessionmaker[Session]:
        connect_args: dict = {}
        if settings.TRINO_PASSWORD:
            connect_args["auth"] = BasicAuthentication(
                settings.TRINO_USER,
                settings.TRINO_PASSWORD,
            )
        engine = create_engine(
            settings.trino_sqlalchemy_url,
            connect_args=connect_args,
            pool_size=settings.TRINO_POOL_SIZE,
            max_overflow=settings.TRINO_POOL_SIZE,
            pool_pre_ping=True,
        )
        return sessionmaker(engine, autoflush=False)

    def get_session(self) -> Session:
        return self._factory()

    def _run(
        self,
        sql: str,
        params: dict[str, Any] | None,
    ) -> tuple[list[str], list[tuple[Any, ...]]]:
        with self._factory() as session:
            result = session.execute(text(sql), params or {})
            columns = list(result.keys())
            rows = result.fetchall()
            return columns, rows

    async def execute(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Executa query e retorna lista de dicts.

        Parâmetros usam estilo nomeado SQLAlchemy: WHERE id = :id
        """
        loop = asyncio.get_running_loop()
        columns, rows = await loop.run_in_executor(
            self._executor, lambda: self._run(sql, params)
        )
        return [dict(zip(columns, row)) for row in rows]

    async def fetch_rows(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]]:
        """Executa query e retorna tuplas brutas."""
        loop = asyncio.get_running_loop()
        _, rows = await loop.run_in_executor(
            self._executor, lambda: self._run(sql, params)
        )
        return rows

    def close(self) -> None:
        self._executor.shutdown(wait=False)
