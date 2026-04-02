from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine
from app.database.models import Base
from app.api.auth_routes import router as auth_router
from app.api.email_routes import router as email_router
from app.api.logs_routes import router as logs_router
from app.api.google_routes import router as google_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.email_routes import poller
import asyncio
import os
print("🚀 APP STARTING...")
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FlowMind AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected")
except Exception as e:
    print("❌ DB ERROR:", e)

app.include_router(auth_router)
app.include_router(google_router)
app.include_router(email_router)
app.include_router(logs_router)
app.include_router(dashboard_router)

# @app.on_event("startup")
# async def start_poller():
#     asyncio.create_task(poller())

@app.get("/")
def root():
    return {"message": "FlowMind AI running"}



if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 5000))  # Render gives PORT
    print(f"🚀 Running on port {port}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )

# uvicorn app.main:app --host localhost --port 8000 --reload 
# curl -X POST https://dominik-imprescriptible-kimberlee.ngrok-free.dev/emails/gmail/webhook ^
# -H "Content-Type: application/json" ^
# -d "{\"message\":{\"data\":\"eyJlbWFpbEFkZHJlc3MiOiJ5b3VyZ21haWxAZ21haWwuY29tIiwiaGlzdG9yeUlkIjoiMTIzIn0=\"}}"

