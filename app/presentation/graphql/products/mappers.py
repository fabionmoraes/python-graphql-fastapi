from app.domain.entities.product import (
    ProductEntity,
    ProductWhereEntity,
    StringComparisonEntity,
)
from app.presentation.graphql.products.types import (
    ProductModelType,
    ProductType,
    ProductWhereInput,
    StringComparisonExp,
)


def to_product_type(product: ProductEntity) -> ProductType:
    related = (
        ProductModelType(
            id=product.product_model.id,
            title=product.product_model.title,
        )
        if product.product_model
        else None
    )
    return ProductType(
        id=product.id,
        name=product.name,
        price=product.price,
        sku=product.sku,
        stock=product.stock,
        product_model=related,
    )


def to_string_comparison(filter_exp: StringComparisonExp | None) -> StringComparisonEntity | None:
    if filter_exp is None:
        return None
    return StringComparisonEntity(
        eq=filter_exp._eq,
        like=filter_exp._like,
        one_of=filter_exp._in,
    )


def to_product_where_entity(where: ProductWhereInput | None) -> ProductWhereEntity | None:
    if where is None:
        return None
    return ProductWhereEntity(
        name=to_string_comparison(where.name),
        sku=to_string_comparison(where.sku),
        model_title=to_string_comparison(where.model_title),
    )
