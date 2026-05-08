from functools import partial

from strawberry.dataloader import DataLoader

from app.core.container import Container
from app.domain.entities.product import ProductEntity


class Loaders:
    def __init__(self, container: Container) -> None:
        self._container = container
        self._products_by_catalog: DataLoader[int, list[ProductEntity]] | None = None

    def get_products_by_catalog(self, selected_fields: dict) -> DataLoader[int, list[ProductEntity]]:
        if self._products_by_catalog is None:
            self._products_by_catalog = DataLoader(
                load_fn=partial(
                    self._container.product_service.list_by_catalog_ids_grouped,
                    selected_fields=selected_fields,
                )
            )
        return self._products_by_catalog
