from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CreateOrderInputValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: Annotated[int, Field(gt=0)]
    quantity: Annotated[int, Field(gt=0, le=10_000)]
    total_price: Annotated[float, Field(gt=0, le=10_000_000)]
