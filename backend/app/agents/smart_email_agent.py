from app.database.models import (
    Email,
    CategoryEnum,
    Complaint,
    RefundRequest,
    ReturnRequest,
    OrderStatus,
    ProductQuestion,
    ExchangeRequest
)
from app.agents.monitor_agent import monitor_agent
from app.services.structured_llm_services import smart_email_llm
import time

PROMPT = """
You are an ecommerce email AI system.

Your job:
1. Classify the email
2. Extract relevant fields

Valid categories:
- complaint
- refund_request
- return_request
- order_status
- product_question
- exchange_request
- general
- others

Rules:
- Return ONLY structured data
- Missing fields must be null
- Never hallucinate values

Subject: {subject}

Body:
{body}
"""


def smart_email_agent(state, db):
    start = time.perf_counter()

    try:
        subject = state["subject"]
        body = state["email_body"]


        result = smart_email_llm.invoke(
            PROMPT.format(
                subject=subject,
                body=body
            )
        )

        data = result.model_dump()

        category = data["category"]

        valid_categories = {
            "complaint",
            "refund_request",
            "return_request",
            "order_status",
            "product_question",
            "exchange_request",
            "general",
            "others"
        }

        if category not in valid_categories:
            category = "others"

        state["category"] = category
        state["extracted"] = data

        email = state["email_obj"]

        if email:
            try:
                email.category = CategoryEnum(category)
            except:
                email.category = CategoryEnum.others

        

        org_id = state["org_id"]
        email_id = state["email_id"]
        sender_email = state["sender_email"]

        obj = None

        if category == "complaint":
            obj = Complaint(
                org_id=org_id,
                email_id=email_id,
                order_id=data.get("order_id"),
                customer_email=sender_email,
                issue_type=data.get("issue_type")
            )

        elif category == "refund_request":
            obj = RefundRequest(
                org_id=org_id,
                email_id=email_id,
                order_id=data.get("order_id"),
                amount=data.get("amount"),
                customer_email=sender_email,
                reason=data.get("reason")
            )

        elif category == "return_request":
            obj = ReturnRequest(
                org_id=org_id,
                email_id=email_id,
                order_id=data.get("order_id"),
                product_name=data.get("product_name"),
                customer_email=sender_email,
                reason=data.get("reason")
            )

        elif category == "order_status":
            obj = OrderStatus(
                org_id=org_id,
                email_id=email_id,
                order_id=data.get("order_id"),
                customer_email=sender_email,
                query=data.get("query")
            )

        elif category == "product_question":
            obj = ProductQuestion(
                org_id=org_id,
                email_id=email_id,
                product_name=data.get("product_name"),
                customer_email=sender_email,
                question=data.get("question")
            )

        elif category == "exchange_request":
            obj = ExchangeRequest(
                org_id=org_id,
                email_id=email_id,
                order_id=data.get("order_id"),
                product_name=data.get("product_name"),
                from_variant=data.get("from_variant"),
                to_variant=data.get("to_variant"),
                reason=data.get("reason"),
                customer_email=sender_email
            )

        if obj:
            db.add(obj)
        
        db.commit()

        monitor_agent(
            "success",
            f"Processed as {category}"
        )

    except Exception as e:

        db.rollback()

        state["category"] = "others"

        monitor_agent(
            "error",
            str(e)
        )
    end = time.perf_counter()

    print(
        f"🧠 Smart Email Agent: {round(end-start,2)}s"
    )
    return state