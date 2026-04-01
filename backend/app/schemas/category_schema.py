from pydantic import BaseModel
from typing import Optional

class ComplaintSchema(BaseModel):
    order_id: Optional[str]
    issue_type: Optional[str]

class RefundSchema(BaseModel):
    order_id: Optional[str]
    amount: Optional[str]
    reason: Optional[str]

class ReturnSchema(BaseModel):
    order_id: Optional[str]
    product_name: Optional[str]
    reason: Optional[str]

class OrderStatusSchema(BaseModel):
    order_id: Optional[str]
    query: Optional[str]


class ProductQuestionSchema(BaseModel):
    product_name: Optional[str]
    question: Optional[str]

class ExchangeSchema(BaseModel):
    order_id: Optional[str]
    product_name: Optional[str]
    from_variant: Optional[str]
    to_variant: Optional[str]
    reason: Optional[str]