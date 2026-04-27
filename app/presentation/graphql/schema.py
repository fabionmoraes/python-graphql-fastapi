import strawberry

from app.presentation.graphql.orders.mutations import OrderMutation
from app.presentation.graphql.orders.queries import OrderQuery
from app.presentation.graphql.products.mutations import ProductMutation
from app.presentation.graphql.products.queries import ProductQuery
from app.presentation.graphql.users.mutations import UserMutation
from app.presentation.graphql.users.queries import UserQuery


@strawberry.type
class Query(ProductQuery, UserQuery, OrderQuery):
    pass


@strawberry.type
class Mutation(ProductMutation, UserMutation, OrderMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
