from graphql import GraphQLError
from pydantic import ValidationError


def raise_graphql_validation_error(exc: ValidationError) -> None:
    details = "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    )
    raise GraphQLError(f"Invalid input data. {details}")
