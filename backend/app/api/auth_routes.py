from fastapi import APIRouter, Form,File,UploadFile,Depends, HTTPException,Request
from fastapi.responses import JSONResponse
from app.schemas.org_schema import OrgLogin
from app.database.db import get_db
from app.database.models import Org
from sqlalchemy.orm import Session
import bcrypt
import fitz
from jose import jwt
from datetime import datetime, timedelta
import os
from fastapi.security import HTTPBearer
from jose import jwt
from app.services.rag_services import store_policy


SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

security = HTTPBearer()


def get_current_org(request: Request):
    print("COOKIES:", request.cookies)
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("JWT payload:", payload)
    return payload["org_id"]

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=2)
    payload.update({"exp": expire})
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def extract_pdf_text(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        text += page.get_text()

    return text

@router.post("/signup")
async def signup(
    orgname:str = Form(...),
    email:str = Form(...),
    password:str = Form(...),
    db: Session = Depends(get_db)
    ):
    print("signup_reached")
    existingemail = db.query(Org).filter(Org.email == email).first()
    if existingemail:
        raise HTTPException(status_code=400, detail="Email already exists")

    if not email or '@' not in email:
        raise HTTPException(status_code=400, detail="Invalid Email")

    if not password or len(password) < 8:
        raise HTTPException(status_code=400, detail="Password should have atleast 8 characters")
 
    salt = bcrypt.gensalt(rounds=10)
    password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    new_org = Org(
        orgname=orgname,
        email=email,
        password=password_hash
    )
    print(new_org)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    token = create_access_token({
        "org_id": new_org.id,
        "email": new_org.email
    })

    response = JSONResponse({
        "message": "User registered successfully"
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,   
        path="/"
    )

    return response

@router.post("/settings")
async def settings(
    policyfile: UploadFile = File(...),
 
    org_id: int = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    print(org_id)
    org = db.query(Org).filter(Org.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    pdf_bytes = await policyfile.read()
    policy_text = extract_pdf_text(pdf_bytes)

    org.policy_text = policy_text
    store_policy(org.id, policy_text)

    print(org_id)
    db.commit()
    print("settings done")
    return {"message": "Settings saved"}



@router.post("/login")
async def Login(
    org:OrgLogin,
    db: Session = Depends(get_db)
):
    existingOrg = db.query(Org).filter(Org.email==org.email).first()
    if not existingOrg:
        raise HTTPException(status_code=400,detail="Invalid email")
    
    if not bcrypt.checkpw(org.password.encode(), existingOrg.password.encode()):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    token = create_access_token({
        "org_id": existingOrg.id,
        "email": existingOrg.email
    })
    response = JSONResponse({
        "message": "User registered successfully"
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,   
        path="/"
    )

    return response


from app.database.models import Org

@router.get("/me")
def get_current_user(
    org_id: int = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    org = db.query(Org).filter(Org.id == org_id).first()

    if not org:
        raise HTTPException(status_code=404, detail="Org not found")

    return {
        "org_id": org.id,
        "orgname": org.orgname,
        "email": org.email,
        "mode": org.mode,
        "gmail_connected": org.gmail_connected
    }