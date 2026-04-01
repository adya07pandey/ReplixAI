from app.services.rag_services import retrieve_context
from app.schemas.email_schema import ReplySchema
from app.database.models import Email
from langchain_groq import ChatGroq
from app.agents.monitor_agent import monitor_agent
import json,re

TONE_MAP = {
    "order_status": "reassuring, informative, and calm",
    "return_request": "helpful, polite, and process-oriented",
    "exchange_request": "solution-oriented, friendly, and supportive",
    "refund_request": "clear, professional, and policy-driven",
    "product_question": "informative, friendly, and engaging",
    "complaint": "empathetic, apologetic, and reassuring",
    "general": "friendly, helpful, and conversational",
    "others": "neutral, polite, and professional"
}
REPLY_PROMPT = """
    You are a professional customer support assistant.
    Write a reply email.
    Tone: {tone}

    Context:
    {context}

    Customer Email:
    Subject: {subject}
    Body: {body}

    Extracted Details:
    {json.dumps(extracted)}

    Category: {category}

    """


def generate_reply(state, db):
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.4
    )

    category = state["category"]
    subject = state["subject"]
    body = state["email_body"]
    org_id = state["org_id"]
    email_id = state["email_id"]
    extracted = state.get("extracted", {})

    # 🧾 START LOG
    state = monitor_agent(
        state, db,
        "reply_agent",
        "start",
        f"Generating reply for {category}"
    )

    try:
        # 🔍 Retrieve context
        query = f"{category} policy {body}"
        context = retrieve_context(org_id, query)

        if not context:
            context = "No specific policy found. Provide a helpful response and ask for any missing details politely."

            state = monitor_agent(
                state, db,
                "reply_agent",
                "warning",
                "No policy context found"
            )
        else:
            state = monitor_agent(
                state, db,
                "reply_agent",
                "info",
                "Policy context retrieved"
            )

        tone = TONE_MAP.get(category, "polite and professional")

        structured_llm = llm.with_structured_output(ReplySchema)

        result = structured_llm.invoke(
            f"""
            You are a professional customer support assistant.

            Tone: {tone}

            Context:
            {context}

            Customer Email:
            Subject: {subject}
            Body: {body}

            Extracted Details:
            {json.dumps(extracted)}

            Category: {category}

            Write a concise reply email (5-8 lines).
            """
        )

        state["reply_subject"] = result.reply_subject
        state["reply_body"] = result.reply_body

        # 🧾 Log reply generated
        state = monitor_agent(
            state, db,
            "reply_agent",
            "success",
            "Reply generated",
            data={"subject": state["reply_subject"]}
        )

    except Exception as e:
        print("❌ LLM failed:", str(e))

        state["reply_subject"] = f"Re: {subject}"
        state["reply_body"] = "Thank you for contacting us. We will get back to you shortly."

        state = monitor_agent(
            state, db,
            "reply_agent",
            "error",
            f"LLM failed: {str(e)}"
        )

    # ❗ DON'T return yet — let DB save fallback reply

    # 💾 Save to DB
    try:
        email = db.query(Email).filter(Email.id == email_id).first()

        if email:
            email.reply_subject = state["reply_subject"]
            email.reply_body = state["reply_body"]
            email.is_replied = False

            db.commit()

            state = monitor_agent(
                state, db,
                "reply_agent",
                "success",
                "Reply saved to DB"
            )

    except Exception as e:
        db.rollback()

        state = monitor_agent(
            state, db,
            "reply_agent",
            "error",
            f"DB save failed: {str(e)}"
        )

    return state