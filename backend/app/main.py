# print("🚀 Step 1: Starting file")

# from dotenv import load_dotenv
# load_dotenv()
# print("✅ Step 2: ENV loaded")

# from fastapi import FastAPI
# print("✅ Step 3: FastAPI imported")

# try:
#     from app.database.db import engine
#     print("✅ Step 4: DB imported")
# except Exception as e:
#     print("❌ DB import failed:", e)
#     raise e

# try:
#     from app.database.models import Base
#     print("✅ Step 5: Models imported")
# except Exception as e:
#     print("❌ Models import failed:", e)
#     raise e

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "running"}


print("🚀 Starting import phase...")

from fastapi import FastAPI
print("✅ FastAPI imported")

from app.database.db import engine
print("✅ DB imported")

from app.database.models import Base
print("✅ Models imported")

from fastapi.middleware.cors import CORSMiddleware
print("✅ cors imported")
# from app.api.auth_routes import router as auth_router
# print("✅ router imported")
    # from app.api.email_routes import router as email_router
    # from app.api.logs_routes import router as logs_router
    # from app.api.google_routes import router as google_router
    # from app.api.dashboard_routes import router as dashboard_router

#     from dotenv import load_dotenv
#     import os

#     load_dotenv()

app = FastAPI(title="FlowMind AI")

#     # app.add_middleware(
#     #     CORSMiddleware,
#     #     allow_origins=["*"],
#     #     allow_credentials=True,
#     #     allow_methods=["*"],
#     #     allow_headers=["*"],
#     # )

# print("🚀 Creating DB...")
# Base.metadata.create_all(bind=engine)
# print("✅ Database connected")

#     # app.include_router(auth_router)
#     # app.include_router(google_router)
#     # app.include_router(email_router)
#     # app.include_router(logs_router)
#     # app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"message": "FlowMind AI running"}

# except Exception as e:
#     import traceback
#     print("❌ FULL ERROR:")
#     traceback.print_exc()

# # uvicorn app.main:app --host localhost --port 8000 --reload 
# # curl -X POST https://dominik-imprescriptible-kimberlee.ngrok-free.dev/emails/gmail/webhook ^
# # -H "Content-Type: application/json" ^
# # -d "{\"message\":{\"data\":\"eyJlbWFpbEFkZHJlc3MiOiJ5b3VyZ21haWxAZ21haWwuY29tIiwiaGlzdG9yeUlkIjoiMTIzIn0=\"}}"

