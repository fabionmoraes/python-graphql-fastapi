from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

SafeText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
SafeSku = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
]


class CreateProductInputValidator(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: SafeText
    price: Annotated[float, Field(gt=0, le=1_000_000)]
    sku: SafeSku
    stock: Annotated[int, Field(ge=0, le=1_000_000)] = 0
    product_model_id: Annotated[int | None, Field(gt=0)] = None
