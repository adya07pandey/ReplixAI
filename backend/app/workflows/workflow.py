from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.database.db import get_db

from app.agents.smart_email_agent import smart_email_agent
from app.agents.reply_agent import generate_reply


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
    sender_name: str | None
    sender_email: str | None
    subject: str | None

    category: str | None

    extracted: dict | None

    reply_subject: str | None
    reply_body: str | None

    logs: list[dict] | None


workflow = StateGraph(WorkflowState)

workflow.add_node("smart_email", with_db(smart_email_agent))
workflow.add_node("reply", with_db(generate_reply))

workflow.set_entry_point("smart_email")

workflow.add_edge("smart_email", "reply")
workflow.add_edge("reply", END)

app = workflow.compile()