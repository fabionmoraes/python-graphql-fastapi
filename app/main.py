from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.security import HTTPBasicCredentials
from strawberry.fastapi import GraphQLRouter

from app.core.container import Container
from app.core.dependencies import require_basic_auth
from app.infrastructure.graphql.loaders import Loaders
from app.infrastructure.graphql.schema import schema
from app.infrastructure.trino.ibis_client import IbisClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.client = IbisClient()
    try:
        yield
    finally:
        app.state.client.close()


app = FastAPI(
    title="GraphQL Python + FastAPI + Trino",
    lifespan=lifespan,
)


async def get_graphql_context(
    request: Request,
    _: HTTPBasicCredentials = Depends(require_basic_auth),
) -> dict:
    client: IbisClient = request.app.state.client
    container = Container(client)
    return {
        "request": request,
        "container": container,
        "loaders": Loaders(container),
    }


graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)
app.include_router(graphql_app, prefix="/graphql")
