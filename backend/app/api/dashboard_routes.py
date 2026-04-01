from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database.db import get_db
from app.database.models import Email
from sqlalchemy import case
from collections import defaultdict
from app.database.models import Complaint, RefundRequest
import os
from jose import jwt

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

def get_current_org(request: Request):
    print("COOKIES:", request.cookies)
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("JWT payload:", payload)
    return payload["org_id"]

def normalize_category(cat):
    if hasattr(cat, "value"):
        return cat.value
    return str(cat).split(".")[-1]
@router.get("")
def get_dashboard(
    org_id: int = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    print("get dashboard")

    # 🔹 TOTAL EMAILS
    total_emails = db.query(func.count(Email.id))\
        .filter(Email.org_id == org_id).scalar()

    # 🔹 SENT EMAILS
    sent = db.query(func.count(Email.id))\
        .filter(
            Email.org_id == org_id,
            Email.status == "sent"
        ).scalar()

    # 🔹 PENDING SEND
    pending = db.query(func.count(Email.id))\
        .filter(
            Email.org_id == org_id,
            Email.status != "sent"
        ).scalar()

    # 🔹 TODAY EMAILS
    today_start = datetime.utcnow().date()

    today = db.query(func.count(Email.id))\
        .filter(
            Email.org_id == org_id,
            func.date(Email.created_at) == today_start
        ).scalar()

    # 📊 CATEGORY BREAKDOWN
    category_data = db.query(
        Email.category,
        func.count(Email.id)
    ).filter(Email.org_id == org_id)\
     .group_by(Email.category).all()

    category_breakdown = [
    {
        "category": normalize_category(cat),
        "count": count
    }
    for cat, count in category_data
]

    # 📈 EMAIL VOLUME
    last_7_days = datetime.utcnow() - timedelta(days=7)

    volume_data = db.query(
        func.date(Email.created_at),
        func.count(Email.id)
    ).filter(
        Email.org_id == org_id,
        Email.created_at >= last_7_days
    ).group_by(func.date(Email.created_at)).all()

    email_volume = [
        {"date": str(date), "count": count}
        for date, count in volume_data
    ]

    # 📊 CATEGORY RESPONSE %
    category_stats = db.query(
        Email.category,
        func.count(Email.id).label("total"),
        func.sum(
            case(
                (Email.status == "sent", 1),
                else_=0
            )
        ).label("sent")
    ).filter(
        Email.org_id == org_id
    ).group_by(Email.category).all()

    category_response = [
        {
            "category": cat.value,
            "total": total_count,
            "sent": sent_count,
            "percent": int((sent_count / total_count) * 100) if total_count > 0 else 0
        }
        for cat, total_count, sent_count in category_stats
    ]

    # 🔥 TOP REASONS

    # Complaint reasons
    complaints = db.query(
        Complaint.issue_type,
        func.count(Complaint.id)
    ).filter(
        Complaint.org_id == org_id
    ).group_by(Complaint.issue_type).all()

    complaint_total = sum(count for _, count in complaints)

    complaint_reasons = [
        {
            "reason": issue,
            "percent": int((count / complaint_total) * 100)
        }
        for issue, count in complaints if issue and complaint_total > 0
    ]

    # Refund reasons
    refunds = db.query(
        RefundRequest.reason,
        func.count(RefundRequest.id)
    ).filter(
        RefundRequest.org_id == org_id
    ).group_by(RefundRequest.reason).all()

    refund_total = sum(count for _, count in refunds)

    refund_reasons = [
        {
            "reason": reason[:30],
            "percent": int((count / refund_total) * 100)
        }
        for reason, count in refunds if reason and refund_total > 0
    ]
    response_rate = int((sent / total_emails) * 100) if total_emails > 0 else 0
    top_category = max(category_breakdown, key=lambda x: x["count"], default=None)

    category_load = {
        "category": top_category["category"] if top_category else None,
        "percent": int((top_category["count"] / total_emails) * 100) if top_category and total_emails > 0 else 0
    }
    all_reasons = []

    for cat, reasons in {
        "complaint": complaint_reasons,
        "refund_request": refund_reasons
    }.items():
        for r in reasons:
            all_reasons.append(r)

    top_issue = max(all_reasons, key=lambda x: x["percent"], default=None)

    pending_pressure = int((pending / total_emails) * 100) if total_emails > 0 else 0

    yesterday_start = datetime.utcnow().date() - timedelta(days=1)

    yesterday = db.query(func.count(Email.id))\
        .filter(
            Email.org_id == org_id,
            func.date(Email.created_at) == yesterday_start
        ).scalar()

    trend = 0
    if yesterday > 0:
        trend = int(((today - yesterday) / yesterday) * 100)
        today_categories = db.query(
    Email.category,
    func.count(Email.id)
    ).filter(
        Email.org_id == org_id,
        func.date(Email.created_at) == today_start
    ).group_by(Email.category).all()

    yesterday_categories = db.query(
        Email.category,
        func.count(Email.id)
    ).filter(
        Email.org_id == org_id,
        func.date(Email.created_at) == yesterday_start
    ).group_by(Email.category).all()

    yesterday_map = {normalize_category(cat): count for cat, count in yesterday_categories}

    category_trend = []

    for cat, count in today_categories:
        cat = normalize_category(cat)
        prev = yesterday_map.get(cat, 0)

        change = int(((count - prev) / prev) * 100) if prev > 0 else 100

        category_trend.append({
            "category": cat,
            "change": change
        })

    hour_data = db.query(
    func.extract("hour", Email.created_at),
    func.count(Email.id)
    ).filter(
        Email.org_id == org_id,
        Email.created_at >= last_7_days
    ).group_by(func.extract("hour", Email.created_at)).all()

    peak_hour = max(hour_data, key=lambda x: x[1], default=None)

    peak_time = {
        "hour": int(peak_hour[0]) if peak_hour else None,
        "count": peak_hour[1] if peak_hour else 0
    }

    hour_data = db.query(
    func.extract("hour", Email.created_at),
    func.count(Email.id)
    ).filter(
        Email.org_id == org_id,
        Email.created_at >= last_7_days
    ).group_by(func.extract("hour", Email.created_at)).all()

    peak_hour = max(hour_data, key=lambda x: x[1], default=None)

    peak_time = {
        "hour": int(peak_hour[0]) if peak_hour else None,
        "count": peak_hour[1] if peak_hour else 0
    }

    today_top_category = max(today_categories, key=lambda x: x[1], default=None)

    today_focus = {
        "category": normalize_category(today_top_category[0]) if today_top_category else None,
        "count": today_top_category[1] if today_top_category else 0
    }

    return {
        "stats": {
            "total": total_emails,
            "today": today,
            "pending": pending,
            "sent": sent
        },
        "category_breakdown": category_breakdown,
        "email_volume": email_volume,
        "category_response": category_response,
        "top_reasons": {
            "complaint": complaint_reasons,
            "refund_request": refund_reasons
        },
        "insights": {
            "response_rate": response_rate,
            "category_load": category_load,
            "top_issue": top_issue,
            "pending_pressure": pending_pressure,
            "trend": trend,
            "category_trend": category_trend,
            "peak_time": peak_time,
            "today_focus": today_focus
        }
    }