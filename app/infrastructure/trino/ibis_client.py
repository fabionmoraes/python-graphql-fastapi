from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import ibis
import ibis.expr.types as ir
import pandas as pd

from app.core.config import settings

try:
    from trino.auth import BasicAuthentication
except ImportError:
    BasicAuthentication = None  # type: ignore[assignment,misc]


class IbisClient:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=settings.TRINO_POOL_SIZE,
            thread_name_prefix="trino",
        )
        auth = (
            BasicAuthentication(settings.TRINO_USER, settings.TRINO_PASSWORD)
            if settings.TRINO_PASSWORD and BasicAuthentication is not None
            else None
        )
        self._con = ibis.trino.connect(
            user=settings.TRINO_USER,
            auth=auth,
            host=settings.TRINO_HOST,
            port=settings.TRINO_PORT,
            http_scheme=settings.TRINO_HTTP_SCHEME,
        )
        self._table_cache: dict[tuple[str, tuple[str, str]], ir.Table] = {}

    def table(self, name: str, database: tuple[str, str]) -> ir.Table:
        key = (name, database)
        if key not in self._table_cache:
            self._table_cache[key] = self._con.table(name, database=database)
        return self._table_cache[key]

    async def execute(self, expr: ir.Table) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()
        df = await loop.run_in_executor(self._executor, expr.execute)
        return _df_to_records(df)

    async def execute_scalar(self, expr: ir.Scalar) -> Any:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(self._executor, expr.execute)
        if hasattr(result, "item"):
            return result.item()
        return result

    def close(self) -> None:
        self._executor.shutdown(wait=False)


def _df_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    result = []
    for record in df.to_dict(orient="records"):
        clean: dict[str, Any] = {}
        for k, v in record.items():
            if v is None:
                clean[k] = None
            elif hasattr(v, "item"):
                clean[k] = None if pd.isna(v) else v.item()
            elif isinstance(v, float) and pd.isna(v):
                clean[k] = None
            else:
                clean[k] = v
        result.append(clean)
    return result
