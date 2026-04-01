from app.agents.monitor_agent import monitor_agent

def email_agent(state, db):

    state = monitor_agent(state, db, "email_agent", "start", "Normalizing email input")

    try:
        state["email_body"] = state.get("email_body", "").strip()
        state["sender_name"] = state.get("sender_name", "")
        state["subject"] = state.get("subject", "")

        state = monitor_agent(
            state,
            db,
            "email_agent",
            "success",
            "Email normalized successfully"
        )

    except Exception as e:
        state = monitor_agent(
            state,
            db,
            "email_agent",
            "error",
            str(e)
        )

    return state