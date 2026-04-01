from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from datetime import datetime
import enum

from app.database.db import Base


class ModeEnum(str, enum.Enum):
    manual = "manual"
    automated = "automated"


class Org(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    orgname = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    policy_text = Column(Text)
    mode = Column(Enum(ModeEnum), default=ModeEnum.manual)

    gmail_access_token = Column(Text)
    gmail_refresh_token = Column(Text)
    gmail_connected = Column(Boolean, default=False)

    gmail_history_id = Column(String)
    gmail_watch_expiry = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class CategoryEnum(str, enum.Enum):
    order_status = "order_status"
    return_request = "return_request"
    exchange_request = "exchange_request"
    refund_request = "refund_request"
    product_question = "product_question"
    complaint = "complaint"
    general = "general"
    others = "others"

class StatusEnum(str,enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    sent = "sent"

class Email(Base):
    __tablename__ = "mails"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"), index=True)
    org = relationship("Org", backref="emails")

    category = Column(Enum(CategoryEnum), nullable=True)

    sender_name = Column(String)
    sender_email = Column(String, nullable=False, index=True)
    sender_subject = Column(String)
    sender_body = Column(Text)

    to_mail = Column(String)

    reply_subject = Column(String)
    reply_body = Column(Text)

    status = Column(Enum(StatusEnum), default=StatusEnum.pending)

    gmail_message_id = Column(String, unique=True, index=True)
    gmail_thread_id = Column(String, index=True)  # 🔥 ADD THIS
    is_replied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    thread_id = Column(String, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        UniqueConstraint("message_id", "org_id", name="unique_message_per_org"),
    )
    org = relationship("Org", backref="processed_emails")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    
    email_id = Column(Integer, ForeignKey("mails.id"))  # link to original email

    order_id = Column(String, index=True)
    customer_email = Column(Text)
    
    issue_type = Column(String)  # damaged, late, missing etc

    status = Column(String, default="pending") # pending/resolved

    created_at = Column(DateTime, default=datetime.utcnow)


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    email_id = Column(Integer, ForeignKey("mails.id"))

    order_id = Column(String, index=True)
    amount = Column(String)
    customer_email = Column(Text)
    reason = Column(Text)

    status = Column(String, default="pending")  # pending/resolved

    created_at = Column(DateTime, default=datetime.utcnow)


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    email_id = Column(Integer, ForeignKey("mails.id"))

    order_id = Column(String)
    product_name = Column(String)

    reason = Column(Text)
    customer_email = Column(Text)

    status = Column(String, default="pending")  # pending/resolved

    created_at = Column(DateTime, default=datetime.utcnow)


class OrderStatus(Base):
    __tablename__ = "order_status_requests"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    email_id = Column(Integer, ForeignKey("mails.id"))

    order_id = Column(String, index=True)
    customer_email = Column(Text)

    query = Column(Text)  # original question

    status = Column(String, default="pending")  # pending/resolved

    created_at = Column(DateTime, default=datetime.utcnow)


class ProductQuestion(Base):
    __tablename__ = "product_questions"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    email_id = Column(Integer, ForeignKey("mails.id"))

    product_name = Column(String)
    customer_email = Column(String)

    question = Column(Text)

    status = Column(String, default="pending")  # pending/resolved

    created_at = Column(DateTime, default=datetime.utcnow)


class ExchangeRequest(Base):
    __tablename__ = "exchange_requests"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    email_id = Column(Integer, ForeignKey("mails.id"))

    order_id = Column(String, index=True)
    product_name = Column(String)

    from_variant = Column(String)  # e.g., size M
    to_variant = Column(String)    # e.g., size L

    reason = Column(Text)
    customer_email = Column(String)

    status = Column(String, default="pending")  # pending/approved/rejected

    created_at = Column(DateTime, default=datetime.utcnow)


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)

    email_id = Column(Integer, ForeignKey("mails.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))

    agent_name = Column(String)   # classify / extract / reply
    status = Column(String)       # success / error

    message = Column(Text)        # short message
    data = Column(Text)           # JSON string (optional)

    created_at = Column(DateTime, default=datetime.utcnow)