from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from app.database.db import get_db
# ✅ import your NEW agents
from app.agents.email_agent import email_agent
from app.agents.category_agent import category_agent
from app.agents.db_agent import db_agent
from app.agents.reply_agent import generate_reply
from app.agents.monitor_agent import monitor_agent


def with_db(agent_func):
    def wrapper(state):
        db = next(get_db())
        try:
            return agent_func(state, db)
        finally:
            db.close()
    return wrapper


class WorkflowState(TypedDict, total=False):
    org_id: int
    email_id: int

    email_body: str
    sender_name: Optional[str]
    sender_email: Optional[str]
    subject: Optional[str]

    category: Optional[str]

    extracted: Optional[dict]

    reply_subject: Optional[str]
    reply_body: Optional[str]

    logs: Optional[List[dict]]   # ✅ updated (list instead of single log)


workflow = StateGraph(WorkflowState)


# ✅ Nodes
workflow.add_node("email", with_db(email_agent))
workflow.add_node("category", with_db(category_agent))
workflow.add_node("db", with_db(db_agent))
workflow.add_node("reply", with_db(generate_reply))
workflow.add_node("monitor", with_db(monitor_agent))


# ✅ Entry
workflow.set_entry_point("email")


# ✅ Flow
workflow.add_edge("email", "category")
workflow.add_edge("category", "db")
workflow.add_edge("db", "reply")
workflow.add_edge("reply", "monitor")
workflow.add_edge("monitor", END)


# ✅ Compile
app = workflow.compile()