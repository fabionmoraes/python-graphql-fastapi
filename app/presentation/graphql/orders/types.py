import strawberry


@strawberry.type
class OrderType:
    id: int
    product_id: int
    quantity: int
    total_price: float
