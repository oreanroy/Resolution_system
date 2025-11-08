from dataclasses import dataclass

from src.enums import ProductType


@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    product_type: ProductType
