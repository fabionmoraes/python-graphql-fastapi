from app.domain.entities.product import ProductCatalogEntity, ProductEntity
from app.infrastructure.graphql.types.product_type import ProductCatalogType, ProductType


def to_product_type(product: ProductEntity) -> ProductType:
    catalog = (
        ProductCatalogType(id=product.product_catalog.id, title=product.product_catalog.title)
        if product.product_catalog
        else None
    )
    return ProductType(
        id=product.id,
        name=product.name,
        price=product.price,
        sku=product.sku,
        stock=product.stock,
        product_catalog_id=product.product_catalog_id,
        product_catalog=catalog,
    )


def to_catalog_type(catalog: ProductCatalogEntity) -> ProductCatalogType:
    return ProductCatalogType(id=catalog.id, title=catalog.title)
