import requests
from fastapi.responses import RedirectResponse
import urllib.parse
import requests
from app.database.db import get_db
from fastapi import APIRouter, Form,File,UploadFile,Depends, HTTPException
from app.schemas.org_schema import OrgLogin
from app.database.db import get_db
from app.database.models import Org
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
from fastapi import Request
from jose import jwt
router = APIRouter(
    prefix="/auth/google",
    tags=["Email Automation"]
)

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

def get_current_org(request: Request):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # print("JWT payload:", payload)
    return payload["org_id"]



def start_gmail_watch(access_token):

    url = "https://gmail.googleapis.com/gmail/v1/users/me/watch"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "topicName": "projects/gmail-api-project-489812/topics/gmail-email-events",
        "labelIds": ["INBOX"]
    }

    response = requests.post(url, headers=headers, json=data)

    return response.json()


@router.get("")
def connect_gmail(
    org_id: int = Depends(get_current_org)
):

    base_url = "https://accounts.google.com/o/oauth2/v2/auth"

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send",
        "access_type": "offline",
        "prompt": "consent",
        "state": org_id
    }

    query_string = urllib.parse.urlencode(params)
    auth_url = f"{base_url}?{query_string}"
    return RedirectResponse(auth_url)


@router.get("/callback")
def google_callback(
    code: str,
    state: int,
    db: Session = Depends(get_db)
):

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI
    }

    response = requests.post(token_url, data=data)

    tokens = response.json()

    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")

    org = db.query(Org).filter(Org.id == state).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.gmail_access_token = access_token
    if refresh_token:
        org.gmail_refresh_token = refresh_token
    org.gmail_connected = True
    
    watch = start_gmail_watch(access_token)
    print("WATCH RESPONSE:", watch)
    org.gmail_history_id = watch["historyId"]
    expiry = datetime.utcnow() + timedelta(days=7)
    org.gmail_watch_expiry = expiry
    db.commit() 
    print("gmail connected")
    return RedirectResponse("http://localhost:5173/dashboard")

