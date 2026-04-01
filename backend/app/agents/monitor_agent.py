from datetime import datetime
import json
from app.database.models import AgentLog

def monitor_agent(state, db, step="unknown", status="info", message="", data=None):

    email_id = state.get("email_id")
    org_id = state.get("org_id")

    # 🧾 Create log dict (for state)
    log = {
        "time": str(datetime.utcnow()),
        "step": step,
        "status": status,
        "message": message,
        "email_id": email_id
    }

    # 🖨️ print (debug)
    print("📊 Workflow Log:", log)

    # 📌 store in state
    if "logs" not in state:
        state["logs"] = []
    state["logs"].append(log)

    # 💾 store in DB
    try:
        db_log = AgentLog(
            email_id=email_id,
            org_id=org_id,
            agent_name=step,
            status=status,
            message=message,
            data=json.dumps(data) if data else None
        )

        db.add(db_log)
        db.commit()

    except Exception as e:
        db.rollback()
        print("❌ Log DB Error:", str(e))

    return state