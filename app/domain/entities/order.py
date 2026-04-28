from dataclasses import dataclass


@dataclass
class OrderEntity:
    id: int
    product_id: int
    quantity: int
    total_price: float
