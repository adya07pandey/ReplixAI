from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import AgentLog
import json

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


# 🔹 1. Get ALL logs
@router.get("/")
def get_logs(db: Session = Depends(get_db)):

    logs = db.query(AgentLog).order_by(AgentLog.created_at.desc()).all()

    return {
        "logs": [
            {
                "id": log.id,
                "email_id": log.email_id,
                "org_id": log.org_id,
                "agent": log.agent_name,
                "status": log.status,
                "message": log.message,
                "data": json.loads(log.data) if log.data else None,
                "time": log.created_at
            }
            for log in logs
        ]
    }


# 🔹 2. Get logs grouped by agent
@router.get("/agents")
def get_agent_logs(db: Session = Depends(get_db)):

    logs = db.query(AgentLog).order_by(AgentLog.created_at.desc()).all()

    agent_map = {}

    for log in logs:
        if log.agent_name not in agent_map:
            agent_map[log.agent_name] = []

        agent_map[log.agent_name].append({
            "email_id": log.email_id,
            "status": log.status,
            "message": log.message,
            "time": log.created_at
        })

    return {
        "agents": agent_map
    }


@router.get("/email/{email_id}")
def get_logs_by_email(email_id: int, db: Session = Depends(get_db)):

    logs = db.query(AgentLog).filter(
        AgentLog.email_id == email_id
    ).order_by(AgentLog.created_at).all()

    return {
        "email_id": email_id,
        "logs": [
            {
                "agent": log.agent_name,
                "status": log.status,
                "message": log.message,
                "time": log.created_at
            }
            for log in logs
        ]
    }