import os
from langchain_groq import ChatGroq
from app.agents.monitor_agent import monitor_agent
from app.database.models import Email, CategoryEnum

# 🔥 Initialize LLM (do this once)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0  # 🔥 strict classification
)

def category_agent(state, db):

    state = monitor_agent(state, db, "category_agent", "start", "Classifying email")

    email_body = f"{state.get('subject', '')}\n{state.get('email_body', '')}"

    prompt = f"""
You are an email classification system.

Classify the following email into EXACTLY one of these categories:

- order_status
- return_request
- exchange_request
- refund_request
- product_question
- complaint
- general
- others

Rules:
- Return ONLY the category name
- No explanation
- No extra words

Email:
\"\"\"
{email_body}
\"\"\"
"""

    try:
        response = llm.invoke(prompt)
        category = response.content.strip().lower()

        valid_categories = {
            "order_status",
            "return_request",
            "exchange_request",
            "refund_request",
            "product_question",
            "complaint",
            "general",
            "others"
        }

        if category not in valid_categories:
            state = monitor_agent(
                state,
                db,
                "category_agent",
                "warning",
                f"Invalid category from LLM: {category}"
            )
            category = "others"

        state["category"] = category
        
        email = db.query(Email).filter(Email.id == state["email_id"]).first()
        
        if not email:
            print("❌ Email not found for id:", state["email_id"])

        if email:
            try:
                email.category = CategoryEnum(state["category"])
            except:
                email.category = CategoryEnum.others

            db.commit()

        state = monitor_agent(
            state,
            db,
            "category_agent",
            "success",
            f"Category detected: {category}"
        )

    except Exception as e:
        state = monitor_agent(
            state,
            db,
            "category_agent",
            "error",
            str(e)
        )
        state["category"] = "others"

    return state