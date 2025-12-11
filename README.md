🚀 ATS Job Application Tracking System (Backend)

A complete Applicant Tracking System (ATS) backend built with FastAPI, PostgreSQL, Celery, and Redis, featuring:

✔ Workflow State Machine

✔ Role-Based Access Control (RBAC)

✔ Asynchronous Email Notifications (Celery + Redis)

✔ Company-based multi-tenant structure

✔ Job CRUD

✔ Application management with history logs

This project fulfills the Partnr GPP "ATS Workflow Backend" task requirements.

📁 Project Structure
app/
├── core/                 # security, RBAC, workflow logic
├── models/               # database models
├── routers/              # API routes
├── schemas/              # Pydantic schemas
├── tasks/                # Celery async email tasks
├── database.py           # DB session + Base
├── main.py               # FastAPI entrypoint
alembic/                  # migrations
celery_app.py             # Celery configuration
.env.example              # environment template
requirements.txt
README.md

🧰 Tech Stack

FastAPI – Backend Framework

PostgreSQL – Database

SQLAlchemy + Alembic – ORM & migrations

Redis – Message broker

Celery – Async worker

JWT Authentication

Passlib/Bcrypt – Password hashing

⚙️ Installation
1️⃣ Clone Repository
git clone https://github.com/prasad5682/ats-job-tracking-system
cd ats-job-tracking-system

2️⃣ Setup Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

🗄️ Database Setup
1️⃣ Create .env File
copy .env.example .env

2️⃣ Edit .env

Example:

DATABASE_URL=postgresql://postgres:password@localhost:5432/atsdb
REDIS_URL=redis://127.0.0.1:6379/0
SECRET_KEY=your_secret_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMAIL_FROM=your@email
SENDGRID_API_KEY=your_key

3️⃣ Create Database
CREATE DATABASE atsdb;

4️⃣ Run Migrations
alembic upgrade head

▶️ Running the Application
Start FastAPI Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


API Docs:

http://127.0.0.1:8000/docs

http://127.0.0.1:8000/redoc

📨 Redis & Celery Setup
Start Redis
Option 1: Local installation
redis-server

Option 2: Docker
docker run -d --name redis -p 6379:6379 redis

Start Celery Worker (Windows Safe)
python -m celery -A celery_app.celery worker --loglevel=info --pool=solo


If successful, you will see:

celery@DESKTOP ready.

🔐 Roles & Permissions (RBAC)
Role	Permissions
Candidate	Apply to jobs, view own applications
Recruiter	Manage jobs, update application stages
Hiring Manager	View all company applications

RBAC is enforced using:

Depends(require_role("candidate", "recruiter"))

🔄 Workflow State Machine

Valid transitions:

Applied → Screening → Interview → Offer → Hired


Reject allowed anytime:

Stage → Rejected


Invalid transitions (e.g., Applied → Offer) produce:

400 Bad Request

📜 Application History Logging

Each stage update stores:

application_id

old_stage

new_stage

changed_by (User ID)

timestamp

This ensures full audit trail visibility.

🧪 API Endpoints
🔐 Authentication
POST /auth/register
POST /auth/login

Register Example
{
  "full_name": "John User",
  "email": "john@example.com",
  "password": "Password123",
  "role": "candidate"
}

Login Example
{
  "email": "john@example.com",
  "password": "Password123"
}


Response:

{
  "access_token": "<TOKEN>",
  "token_type": "bearer",
  "role": "candidate",
  "user_id": 1
}


Use token:

Authorization: Bearer <TOKEN>

🧑‍💼 Jobs (Recruiter Only)
POST /jobs/
GET /jobs/
GET /jobs/{id}
PUT /jobs/{id}
DELETE /jobs/{id}

Create Job Example
{
  "title": "Backend Developer",
  "description": "API development"
}

📄 Applications
POST /applications/apply/{job_id}
PUT /applications/{id}/stage
GET /applications/my
GET /applications/job/{job_id}
GET /applications/company/{company_id}

Change Stage Example
"Interview"

🧪 Testing the System
1️⃣ Start FastAPI & Celery
2️⃣ Register & login recruiter + candidate
3️⃣ Recruiter → Create job
4️⃣ Candidate → Apply to job
5️⃣ Celery SHOULD SHOW:
Received task: send_stage_change_email

6️⃣ Recruiter updates stage

Celery logs again.

7️⃣ Verify application_history table:
SELECT * FROM application_history;

8️⃣ RBAC Tests
Action	Expected
Candidate creates job	❌ 403 Forbidden
Candidate updates stage	❌ 403 Forbidden
Recruiter edits other company job	❌ 403 Forbidden
9️⃣ Workflow Test

Invalid transition must return 400.

🧱 Architecture Diagram
                   +----------------------+
                   |      PostgreSQL      |
                   |  Users, Jobs, Apps   |
                   +----------+-----------+
                              |
                       SQLAlchemy ORM
                              |
                +-------------+--------------+
                |        FastAPI Backend     |
                | Auth • RBAC • Workflow     |
                +-------------+--------------+
                              |
                   (sends email tasks)
                              |
                           Redis Queue
                              |
                     +--------+--------+
                     |    Celery Worker |
                     | Processes Emails |
                     +------------------+













                     