# 🚀 AI Email Automation System

An AI-powered multi-agent email automation system that integrates with Gmail to automatically read, classify, process, and respond to emails using intelligent workflows.

---

## Features

- Google OAuth Integration (Gmail Connect)
- Real-time Email Processing using Webhooks
- Secure Authentication using JWT and Cookies
- Multi-Agent AI System for email processing
- Context-aware Reply Generation
- Category-wise Email Management
- Structured Data Extraction (Refunds, Orders, Complaints, etc.)
- Real-time updates via WebSockets
- Semantic Search using Vector DB (Qdrant)

---

## Multi-Agent Architecture

This project is built using a multi-agent pipeline where each agent performs a specific task:

- Email Agent → Extracts email content  
- Category Agent → Classifies the email  
- DB Agent → Extracts structured data and stores it  
- Reply Agent → Generates AI response  
- Monitor Agent → Tracks logs and execution  

All agents are orchestrated using LangGraph workflows.

---

## How It Works

1. User connects Gmail via OAuth  
2. Gmail sends webhook events for new emails  
3. Backend fetches email data  
4. Multi-agent workflow executes:
   - Classify email
   - Extract structured information
   - Store in database
   - Generate reply  
5. Response is sent or reviewed manually  

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite

### AI / ML
- LangGraph (multi-agent orchestration)
- Groq LLM (LLaMA 3)
- Sentence Transformers

### Database
- Relational DB (Emails, Org, Requests)
- Qdrant (Vector Database)

### Authentication and Security
- JWT (JSON Web Tokens)
- Cookies (Session management)

### Integrations
- Gmail API
- Google OAuth 2.0
- Gmail Webhooks (Pub/Sub)

### Realtime
- WebSockets

---

## Project Structure

```text
app/
│── agents/          # Multi-agent logic (classification, extraction, reply)
│── database/        # DB models and connection
│── routes/          # API routes
│── workflows/       # LangGraph multi-agent workflow
│── services/        # WebSocket manager
│── schemas/         # Pydantic schemas
```


## Workflow Pipeline

Email → Category → DB Extraction → Reply Generation → Monitoring

---

## Email Categories

- Order Status  
- Return Request  
- Exchange Request  
- Refund Request  
- Product Question  
- Complaint  
- General  
- Others  

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/email-automation.git
cd email-automation
```
## Setup Instructions

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env file
```bash
JWT_SECRET=your_secret
JWT_ALGORITHM=HS256

GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_api_key
```
## Authentication Flow
- User logs in and a JWT token is generated
- Token is stored in cookies
- Each request reads the token from cookies
- JWT is decoded to identify the organization

## API Endpoints

### Auth

- GET /auth/google → Connect Gmail  
- GET /auth/google/callback → OAuth callback  

### Emails

- POST /emails/gmail/webhook → Gmail webhook listener  
- GET /emails/category/{category} → Get emails by category  
- GET /emails/mail/{emailid} → Get single email  
- PUT /emails/{email_id} → Update reply  
- POST /emails/send/{email_id} → Send email  

### WebSocket

- WS /emails/ws → Real-time updates  

---

## Real-time Email Processing

- Gmail sends events via Webhooks (Pub/Sub)  
- Backend processes emails instantly  
- Fallback polling runs every 2 minutes  
- WebSocket broadcasts updates to frontend  

---

## Vector Search (RAG)

- Policies are embedded using Sentence Transformers  
- Stored in Qdrant  
- Retrieved during reply generation for better accuracy  

---

## Key Highlights

- Multi-agent AI architecture  
- Idempotent email processing  
- Token auto-refresh for Gmail API  
- Duplicate webhook protection  
- Scalable backend design  
