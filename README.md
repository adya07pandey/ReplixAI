# 🚀 AI Email Automation System

An AI-powered email automation platform that integrates with Gmail to automatically read, classify, process, and respond to emails using intelligent agents and workflows.

---

## ✨ Features

- 🔐 Google OAuth Integration (Gmail Connect)
- 📩 Real-time Email Processing using **Webhooks**
- 🔑 Authentication using **JWT + Cookies**
- 🤖 AI-based Email Classification
- 🧠 Context-aware Reply Generation
- 🗂️ Category-wise Email Management
- 📊 Structured Data Extraction (Refunds, Orders, Complaints, etc.)
- ⚡ Real-time updates via WebSockets
- 📚 Semantic Search using Vector DB (Qdrant)

---

## 🧠 How It Works

1. User connects Gmail via OAuth  
2. Gmail sends webhook events for new emails  
3. Backend fetches and processes emails  
4. AI workflow:
   - Classify email
   - Extract structured data
   - Store in DB
   - Generate reply  
5. Reply is sent or reviewed manually  

---

## 🏗️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite

### AI / ML
- LangGraph (workflow orchestration)
- Groq LLM (LLaMA 3)
- Sentence Transformers

### Database
- Relational DB (Emails, Org, Requests)
- Qdrant (Vector DB)

### Authentication & Security
- JWT (JSON Web Tokens)
- Cookies (Session handling)

### Integrations
- Gmail API
- Google OAuth 2.0
- Gmail Webhooks (Pub/Sub)

### Realtime
- WebSockets

---

## 📂 Project Structure
app/
│── agents/ # AI agents (classification, extraction, reply)
│── database/ # DB models & connection
│── routes/ # API routes
│── workflows/ # LangGraph workflow
│── services/ # WebSocket manager
│── schemas/ # Pydantic schemas


---

## 🔄 Workflow Pipeline
Email → Category → DB Extraction → Reply Generation → Monitoring


---

## 📊 Email Categories

- Order Status  
- Return Request  
- Exchange Request  
- Refund Request  
- Product Question  
- Complaint  
- General / Others  

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/email-automation.git
cd email-automation
