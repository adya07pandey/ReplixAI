from app.services.rag_services import retrieve_context
from app.database.models import Email
from app.agents.monitor_agent import monitor_agent
import json
from app.services.structured_llm_services import reply_llm
import time 

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



def generate_reply(state, db):
    start = time.perf_counter()
    category = state["category"]
    subject = state["subject"]
    body = state["email_body"]
    org_id = state["org_id"]
    email_id = state["email_id"]
    extracted = state.get("extracted", {})


    try:
        
        query = f"{category} policy {body}"
        context = retrieve_context(db, org_id, query)

        if not context:
            context = "No specific policy found. Provide a helpful response and ask for any missing details politely."

        

        tone = TONE_MAP.get(category, "polite and professional")


        result = reply_llm.invoke(
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

    except Exception as e:
        print("❌ LLM failed:", str(e))

        state["reply_subject"] = f"Re: {subject}"
        state["reply_body"] = "Thank you for contacting us. We will get back to you shortly."

       

    try:
        email = state["email_obj"]

        if email:
            email.reply_subject = state["reply_subject"]
            email.reply_body = state["reply_body"]
            email.is_replied = False

            db.commit()

            monitor_agent(
                "success",
                f"Processed as {category}"
            )

    except Exception as e:
        db.rollback()

        monitor_agent(
            "error",
            str(e)
        )
    end = time.perf_counter()

    print(
        f"✉️ Reply Agent: {round(end-start,2)}s"
    )
    return state