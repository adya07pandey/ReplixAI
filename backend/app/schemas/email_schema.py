from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import enum
 

class StatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    sent = "sent"

class CategoryEnum(str, enum.Enum):
    order_status = "order_status"
    return_request = "return_request"
    exchange_request = "exchange_request"
    refund_request = "refund_request"
    product_question = "product_question"
    complaint = "complaint"
    general = "general"
    others="others"

from pydantic import BaseModel, Field


class EmailResponse(BaseModel):
    id: int
    category: str

    sender: str = Field(alias="sender_mail")
    subject: str | None = Field(default=None, alias="sender_subject")
    body: str | None = Field(default=None, alias="sender_body")

    to: str | None = Field(default=None, alias="to_mail")
    reply_subject: str | None = None
    reply_body: str | None = None

    status: StatusEnum | None = None
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class ReplySchema(BaseModel):
    reply_subject: str
    reply_body: str