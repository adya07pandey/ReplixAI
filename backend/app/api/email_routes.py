from app.database.models import Complaint, RefundRequest, ReturnRequest, OrderStatus, ProductQuestion, ExchangeRequest
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Depends, WebSocket
from sqlalchemy.orm import Session
import base64, json, os, requests
from jose import jwt
from app.database.db import SessionLocal,get_db
from app.database.models import Org, Email, ProcessedEmail, CategoryEnum
from app.workflows.workflow import app
from app.services.ws_services import manager
from email.utils import parseaddr
import asyncio

router = APIRouter(
    prefix="/emails",
    tags=["Email Automation"]
)
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def get_current_org(request: Request):
    print("COOKIES:", request.cookies)
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("JWT payload:", payload)
    return payload["org_id"]

# ------------------ TOKEN ------------------ #
def refresh_access_token(refresh_token: str):
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=data, timeout=10)

    if response.status_code != 200:
        print("❌ Refresh failed:", response.text)
        raise Exception("Token refresh failed")

    return response.json()["access_token"]


def get_valid_access_token(org, db: Session):
    if org.gmail_access_token:
        return org.gmail_access_token

    new_token = refresh_access_token(org.gmail_refresh_token)
    org.gmail_access_token = new_token
    db.commit()
    return new_token

async def process_gmail_event(email: str, history_id: str):
    db = SessionLocal()

    try:
        email = email.lower().strip()
        print(f"\n⚙️ Processing webhook for: {email}")

        org = db.query(Org).filter(Org.email == email).first()

        if not org:
            print("❌ Org not found:", email)
            return

        # ✅ duplicate webhook check
        if str(history_id) == str(org.gmail_history_id):
            print("⚠️ Duplicate webhook skipped")
            return

        access_token = get_valid_access_token(org, db)

        # ✅ FIRST TIME SETUP
        if not org.gmail_history_id:
            org.gmail_history_id = history_id
            db.commit()
            print("⚡ First history stored")
            return

        # ✅ IMPORTANT FIX: store old history BEFORE updating
        prev_history_id = org.gmail_history_id

        # ✅ update immediately (prevents reprocessing old messages)
        org.gmail_history_id = history_id
        db.commit()

        # ------------------ FETCH HISTORY ------------------ #
        url = "https://gmail.googleapis.com/gmail/v1/users/me/history"

        params = {
            "startHistoryId": prev_history_id,
            "historyTypes": ["messageAdded"]
        }

        headers = {"Authorization": f"Bearer {access_token}"}

        res = requests.get(url, headers=headers, params=params, timeout=10)

        if res.status_code != 200:
            print("⚠️ Token expired → refreshing")

            access_token = refresh_access_token(org.gmail_refresh_token)
            org.gmail_access_token = access_token
            db.commit()

            headers["Authorization"] = f"Bearer {access_token}"
            res = requests.get(url, headers=headers, params=params, timeout=10)

        history_data = res.json()
        print("📊 History:", history_data)

        if "history" not in history_data:
            print("📭 No new emails")
            return

        seen_messages = set()

        for record in history_data["history"]:
            if "messagesAdded" not in record:
                continue

            for msg in record["messagesAdded"]:
                msg_id = msg["message"]["id"]
                thread_id = msg["message"]["threadId"]

                print(f"🔍 Checking msg_id={msg_id}, thread_id={thread_id}")

                if msg_id in seen_messages:
                    continue
                seen_messages.add(msg_id)

                # ✅ CORRECT idempotency check
                exists = db.query(ProcessedEmail).filter_by(
                    message_id=msg_id,
                    org_id=org.id
                ).first()

                if exists:
                    print(f"⚠️ Skipping already processed message: {msg_id}")
                    continue   # ✅ FIXED (was return)

                # ------------------ FETCH MESSAGE ------------------ #
                msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"

                msg_res = requests.get(
                    msg_url,
                    headers=headers,
                    params={
                        "format": "metadata",
                        "metadataHeaders": ["Subject", "From"]
                    },
                    timeout=10
                )

                if msg_res.status_code != 200:
                    print("❌ Message fetch failed:", msg_res.text)
                    continue

                msg_data = msg_res.json()
                labelIds = msg["message"].get("labelIds", [])

                if "INBOX" not in labelIds:
                    continue

                headers_list = msg_data.get("payload", {}).get("headers", [])
                

                subject = next(
                    (h["value"] for h in headers_list if h["name"] == "Subject"),
                    "No Subject"
                )

                raw_sender = next(
                    (h["value"] for h in headers_list if h["name"] == "From"),
                    "Unknown"
                )

                # extract sender
                sender_name, sender_email = parseaddr(raw_sender)

                # ✅ skip emails sent by org itself
                if sender_email.lower() == org.email.lower():
                    print("⏭ Skipping self email")
                    continue
                
                # fallback safety
                if not sender_email:
                    sender_email = raw_sender

                email_body = msg_data.get("snippet", "")

                # ------------------ STORE EMAIL ------------------ #
                new_email = Email(
                    org_id=org.id,
                    sender_name=sender_name,
                    sender_email=sender_email,
                    sender_subject=subject,
                    sender_body=email_body,
                    status="pending"
                )

                db.add(new_email)
                db.commit()
                db.refresh(new_email)

                # ------------------ WORKFLOW ------------------ #
                result = app.invoke({
                    "org_id": org.id,
                    "email_id": new_email.id,
                    "email_body": email_body,
                    "sender_name": sender_name,
                    "sender_email": sender_email,
                    "subject": subject
                })

                print("\n🤖 WORKFLOW RESULT:", result)
                
                await manager.broadcast({
                        "event": "new_email",
                        "org_id": org.id,
                        "category": result.get("category")
                    })
                
                # ------------------ MARK PROCESSED ------------------ #
                db.add(ProcessedEmail(
                    message_id=msg_id,
                    thread_id=thread_id,
                    org_id=org.id
                ))
                db.commit()

        print("✅ Processing complete")

    except Exception as e:
        print("❌ Background Error:", e)

    finally:
        db.close()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)
# ------------------ WEBHOOK ------------------ #
@router.post("/gmail/webhook")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    print("\n🔔 WEBHOOK HIT")

    try:
        body = await request.json()
    except Exception as e:
        print("⚠️ Body read failed:", e)
        return {"status": "ignored"}

    try:
        message_data = body["message"]["data"]
        decoded = base64.b64decode(message_data).decode("utf-8")
        data = json.loads(decoded)

        email = data["emailAddress"]
        history_id = data["historyId"]

        print("📩 Email:", email)
        print("📌 HistoryId:", history_id)

        # ✅ SAFE BACKGROUND CALL (NO DB PASSED)
        background_tasks.add_task(process_gmail_event, email, history_id)

    except Exception as e:
        print("❌ Webhook Error:", e)

    return {"status": "accepted"}


async def poll_recent_emails(org, db):
    access_token = get_valid_access_token(org, db)

    headers = {"Authorization": f"Bearer {access_token}"}

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

    res = requests.get(
        url,
        headers=headers,
        params={
            "maxResults": 20,
            "q": "newer_than:1d"
        },
        timeout=10
    )

    messages = res.json().get("messages", [])

    for msg in messages:
        msg_id = msg["id"]
        thread_id = msg.get("threadId")

        await process_message_by_id(msg_id, thread_id, org, db, headers)


async def process_message_by_id(msg_id, thread_id, org, db, headers):
    # ✅ skip if already processed
    exists = db.query(ProcessedEmail).filter_by(
        message_id=msg_id,
        org_id=org.id
    ).first()

    if exists:
        return

    # 🔹 fetch message
    msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"

    msg_res = requests.get(
        msg_url,
        headers=headers,
        params={
            "format": "metadata",
            "metadataHeaders": ["Subject", "From"]
        },
        timeout=10
    )

    if msg_res.status_code != 200:
        return

    msg_data = msg_res.json()
    labelIds = msg_data.get("labelIds", [])

    if "INBOX" not in labelIds:
        return
    headers_list = msg_data.get("payload", {}).get("headers", [])

    subject = next((h["value"] for h in headers_list if h["name"] == "Subject"), "")
    raw_sender = next((h["value"] for h in headers_list if h["name"] == "From"), "")

    sender_name, sender_email = parseaddr(raw_sender)
    if sender_email.lower() == org.email.lower():
        return
    email_body = msg_data.get("snippet", "")

    # 🔹 store
    new_email = Email(
        org_id=org.id,
        sender_name=sender_name,
        sender_email=sender_email,
        sender_subject=subject,
        sender_body=email_body,
        status="pending"
    )

    db.add(new_email)
    db.commit()
    db.refresh(new_email)

    # 🔹 workflow
    result = app.invoke({
        "org_id": org.id,
        "email_id": new_email.id,
        "email_body": email_body,
        "sender_name": sender_name,
        "sender_email": sender_email,
        "subject": subject
    })

    await manager.broadcast({
        "event": "new_email",
        "org_id": org.id,
        "category": result.get("category")
    })
    # 🔹 mark processed
    db.add(ProcessedEmail(
        message_id=msg_id,
        thread_id=thread_id,
        org_id=org.id
    ))
    db.commit()

async def poller():
    while True:
        db = SessionLocal()
        try:
            orgs = db.query(Org).all()

            for org in orgs:
                await poll_recent_emails(org, db)

        except Exception as e:
            print("Polling error:", e)
        finally:
            db.close()

        await asyncio.sleep(120)  # 🔥 every 2 min


@router.get("/category/{category}")
async def get_emails(
    category: str,
    org_id: int = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    # model = MODEL_MAP.get(category)

    # if not model:
    #     raise HTTPException(status_code=400, detail="Invalid category")

    data = db.query(Email).filter(Email.category == category).all()
    return data


@router.get("/mail/{emailid}")
async def openMail(
    emailid: int,
    org_id:int = Depends(get_current_org),
    db:Session = Depends(get_db)
):
    data = db.query(Email).filter(
        Email.id == emailid,
        Email.org_id == org_id
    ).first()
    if not data:
        raise HTTPException(status_code=404, detail="Email not found")
    print(data)
    return data

@router.put("/{email_id}")
def update_email(email_id: int, data: dict, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    email.reply_subject = data.get("reply_subject")
    email.reply_body = data.get("reply_body")

    db.commit()
    return {"message": "Updated"}

import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_gmail_service(org, db):
    access_token = get_valid_access_token(org, db)

    creds = Credentials(
        token=access_token,
        refresh_token=org.gmail_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
    )

    return build("gmail", "v1", credentials=creds)
def send_gmail_message(org, db, to, subject, body):
    service = get_gmail_service(org, db)

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

@router.post("/send/{email_id}")
def send_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    org = db.query(Org).filter(Org.id == email.org_id).first()

    # ✅ correct field
    to_email = email.sender_email

    subject = email.reply_subject
    body = email.reply_body

    # 🔥 send email
    send_gmail_message(org, db, to_email, subject, body)

    # ✅ update DB
    email.is_replied = True
    email.status = "sent"

    db.commit()

    return {"message": "Email sent"}