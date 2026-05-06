from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from app.core.container import Container
from app.core.trino import TrinoClient
from app.presentation.graphql.schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.trino = TrinoClient()
    try:
        yield
    finally:
        app.state.trino.close()


app = FastAPI(
    title="GraphQL Python + FastAPI + Trino",
    lifespan=lifespan,
)


async def get_graphql_context(request: Request) -> dict:
    trino: TrinoClient = request.app.state.trino
    return {
        "request": request,
        "container": Container(trino),
    }


graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)
app.include_router(graphql_app, prefix="/graphql")
