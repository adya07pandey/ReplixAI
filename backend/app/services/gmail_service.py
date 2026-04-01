from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from app.database.db import SessionLocal
from app.database.models import Org
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

def get_gmail_service(org_id: int):
    db = SessionLocal()

    org = db.query(Org).filter(Org.id == org_id).first()

    if not org or not org.gmail_access_token:
        db.close()
        raise Exception("Gmail not connected")

    creds = Credentials(
        token=org.gmail_access_token,
        refresh_token=org.gmail_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )

    # 🔥 Auto refresh token
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        org.gmail_access_token = creds.token
        db.commit()

    service = build("gmail", "v1", credentials=creds)

    db.close()
    return service