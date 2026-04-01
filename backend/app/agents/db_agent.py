from app.database.models import Complaint, RefundRequest, ReturnRequest,OrderStatus,ProductQuestion,ExchangeRequest
from app.schemas.category_schema import ComplaintSchema,RefundSchema,ReturnSchema,ExchangeSchema,ProductQuestionSchema,OrderStatusSchema
from langchain_groq import ChatGroq
from app.database.db import get_db
from app.agents.monitor_agent import monitor_agent
import json,re

COMPLAINT_PROMPT = """
Extract complaint details from the email.

Return ONLY valid JSON. No explanation.

Schema:
{
  "order_id": string | null,
  "issue_type": "damaged" | "missing" | "late" | "wrong_item" | "other" | null
}

Rules:
- If a field is NOT present → return null (NOT "", NOT "unknown")
- Do NOT guess values
- Output must be strictly valid JSON
- No markdown, no extra text

Subject: {subject}
Body: {body}
"""
REFUND_PROMPT = """
Extract refund request details.

Return ONLY valid JSON.

Schema:
{
  "order_id": string | null,
  "amount": string | null,
  "reason": string | null
}

Rules:
- If not mentioned → return null
- Amount can be numeric or text (e.g., "500", "full refund")
- Do NOT guess
- Strict JSON only

Subject: {subject}
Body: {body}
"""
RETURN_PROMPT = """
Extract return request details.

Return ONLY valid JSON.

Schema:
{
  "order_id": string | null,
  "product_name": string | null,
  "reason": string | null
}

Rules:
- If missing → return null
- Do NOT assume product names
- Strict JSON only

Subject: {subject}
Body: {body}
"""
ORDER_STATUS_PROMPT = """
Extract order status query.

Return ONLY valid JSON.

Schema:
{
  "order_id": string | null,
  "query": string | null
}

Rules:
- If order_id not mentioned → return null
- Query should summarize user intent (e.g., "delivery status", "tracking info")
- Do NOT hallucinate order_id
- Strict JSON only

Subject: {subject}
Body: {body}
"""
PRODUCT_PROMPT = """
Extract product-related question.

Return ONLY valid JSON.

Schema:
{
  "product_name": string | null,
  "question": string | null
}

Rules:
- Question should summarize user query clearly
- If product not mentioned → null
- Do NOT guess product names
- Strict JSON only

Subject: {subject}
Body: {body}
"""
EXCHANGE_PROMPT = """
Extract exchange request details.

Return ONLY valid JSON.

Schema:
{{
  "order_id": string | null,
  "product_name": string | null,
  "from_variant": string | null,
  "to_variant": string | null,
  "reason": string | null
}}

Rules:
- Exchange = replacement (size, color, variant)
- from_variant = current item (e.g., "size M", "red")
- to_variant = desired item (e.g., "size L", "blue")
- If any field missing → return null
- Do NOT guess values
- Return proper JSON so that we can extract from it using code 
- Return ONLY valid JSON.
- Do NOT include explanation.
- Do NOT include text before or after JSON.
- Ensure JSON is properly formatted.

Subject: {subject}
Body: {body}
"""

def db_agent(state, db):
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )
    # ✅ STEP 1: get values FIRST
    category = state["category"]
    subject = state["subject"]
    body = state["email_body"]
    sender_name = state["sender_name"]
    sender_email = state["sender_email"]
    org_id = state["org_id"]
    email_id = state["email_id"]

    # 🧾 Start log
    state = monitor_agent(state, db, "db_agent", "start", f"Processing {category}")

    # ✅ STEP 2: schema map
    SCHEMA_MAP = {
        "complaint": ComplaintSchema,
        "refund_request": RefundSchema,
        "return_request": ReturnSchema,
        "order_status": OrderStatusSchema,
        "product_question": ProductQuestionSchema,
        "exchange_request": ExchangeSchema
    }

    schema = SCHEMA_MAP[category]

    # ✅ STEP 3: structured LLM
    structured_llm = llm.with_structured_output(schema)

    try:
        result = structured_llm.invoke(
            f"""
            Extract relevant fields from the email.

            Subject: {subject}
            Body: {body}
            """
        )

        extract_res = result.model_dump()

        print("✅ extracted:", extract_res)

        def normalize(val):
            if val in ["", "null", "None", "unknown"]:
                return None
            return val

        extract_res = {k: normalize(v) for k, v in extract_res.items()}

        state = monitor_agent(
            state,
            db,
            "db_agent",
            "success",
            "Extraction done",
            data=extract_res
        )

    except Exception as e:
        print("❌ LLM failed:", str(e))
        state = monitor_agent(
            state,
            db,
            "db_agent",
            "error",
            f"LLM extraction failed: {str(e)}"
        )
        return state

    # 🗄️ DB insert
    try:
        if category == "complaint":
            obj = Complaint(
                org_id=org_id,
                email_id=email_id,
                order_id=extract_res.get("order_id"),
                customer_email=sender_email,
                issue_type=extract_res.get("issue_type")
            )

        elif category == "refund_request":
            obj = RefundRequest(
                org_id=org_id,
                email_id=email_id,
                order_id=extract_res.get("order_id"),
                amount=extract_res.get("amount"),
                customer_email=sender_email,
                reason=extract_res.get("reason")
            )

        elif category == "return_request":
            obj = ReturnRequest(
                org_id=org_id,
                email_id=email_id,
                order_id=extract_res.get("order_id"),
                product_name=extract_res.get("product_name"),
                customer_email=sender_email,
                reason=extract_res.get("reason")
            )

        elif category == "order_status":
            obj = OrderStatus(
                org_id=org_id,
                email_id=email_id,
                order_id=extract_res.get("order_id"),
                customer_email=sender_email,
                query=extract_res.get("query")
            )

        elif category == "product_question":
            obj = ProductQuestion(
                org_id=org_id,
                email_id=email_id,
                product_name=extract_res.get("product_name"),
                customer_email=sender_email,
                question=extract_res.get("question")
            )

        elif category == "exchange_request":
            obj = ExchangeRequest(
                org_id=org_id,
                email_id=email_id,
                order_id=extract_res.get("order_id"),
                product_name=extract_res.get("product_name"),
                from_variant=extract_res.get("from_variant"),
                to_variant=extract_res.get("to_variant"),
                reason=extract_res.get("reason"),
                customer_email=sender_email
            )

        db.add(obj)
        db.commit()

        # 🧾 Success log
        state = monitor_agent(
            state,
            db,
            "db_agent",
            "success",
            f"{category} stored successfully"
        )

    except Exception as e:
        db.rollback()

        state = monitor_agent(
            state,
            db,
            "db_agent",
            "error",
            f"DB insert failed: {str(e)}"
        )
    state["extracted"] = extract_res
    return state