from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter

from app.core.database import Base, engine
from app.core.dependencies import get_db
from app.infrastructure.persistence.models.order_model import OrderModel
from app.infrastructure.persistence.models.product_model import ProductModel
from app.infrastructure.persistence.models.user_model import UserModel
from app.presentation.graphql.schema import schema

# Force model imports for metadata registration.
_ = (UserModel, ProductModel, OrderModel)

app = FastAPI(title="GraphQL Python + FastAPI + SQLAlchemy + JWT")
Base.metadata.create_all(bind=engine)


def get_graphql_context(request: Request, db: Session = Depends(get_db)) -> dict:
    return {"request": request, "db": db}


graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)
app.include_router(graphql_app, prefix="/graphql")
