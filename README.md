🚀 ATS Job Application Tracking System (Backend)

A complete Applicant Tracking System (ATS) backend built using FastAPI, PostgreSQL, Celery, and Redis, implementing:

✔ Workflow State Machine

✔ Role-Based Access Control (RBAC)

✔ Asynchronous Email Notifications (Celery + Redis)

✔ Multi-tenant Companies with Recruiters & Hiring Managers

✔ Job CRUD

✔ Application management with full audit history

This project fulfills the Partnr GPP: Workflow + ATS Backend Development task.

📁 Project Structure
app/
├── core/                 # security, rbac, workflow logic
├── models/               # database models
├── routers/              # API routes
├── schemas/              # Pydantic schemas
├── tasks/                # Celery async email tasks
├── database.py           # DB session + Base
├── main.py               # FastAPI entrypoint
celery_app.py             # Celery configuration
alembic/                  # DB migrations
.env.example              # environment template
requirements.txt

🧰 Tech Stack

FastAPI – backend framework

PostgreSQL – relational database

SQLAlchemy + Alembic – ORM + migrations

Redis – message broker

Celery – async task queue

JWT Authentication – secure login

Passlib (bcrypt) – password hashing

⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/prasad5682/ats-job-tracking-system
cd ats-job-tracking-system

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

🗄️ Database Setup
1. Create .env file

Copy the example:

copy .env.example .env   # Windows

2. Set values inside .env

Example:

DATABASE_URL=postgresql://postgres:password@localhost:5432/atsdb
REDIS_URL=redis://127.0.0.1:6379/0
SECRET_KEY=your_secret_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMAIL_FROM=your@email
SENDGRID_API_KEY=your_key

3. Create Database
CREATE DATABASE atsdb;

4. Run Migrations
alembic upgrade head

▶️ Running the Application
Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


API docs available at:

👉 http://127.0.0.1:8000/docs

👉 http://127.0.0.1:8000/redoc

📨 Start Redis (message broker)
If Redis installed locally
redis-server

Or via Docker
docker run -d --name redis -p 6379:6379 redis

🟢 Start Celery Worker (Windows Compatible)
python -m celery -A celery_app.celery worker --loglevel=info --pool=solo


Celery must show:

celery@DESKTOP ready.

🔐 Roles & Permissions (RBAC)
Role	Permissions
Candidate	Apply to jobs, view their applications
Recruiter	Create/update/delete jobs, manage applicants
Hiring Manager	View all company applications
Admin (optional)	Full access

RBAC implemented via:

Depends(require_role("candidate", "recruiter"))

🔄 Workflow State Machine

Valid Stage Flow:

Applied → Screening → Interview → Offer → Hired


Rejected allowed from any stage:

Stage → Rejected


Invalid transitions (e.g., Applied → Offer) return:

400 Bad Request

📝 Application History Logging

Every stage change inserts a record with:

application_id

old_stage

new_stage

changed_by (user ID)

timestamp

This maintains a full audit trail.

🧪 API Endpoints
🔐 Authentication
POST /auth/register
POST /auth/login

Register Example
{
  "full_name": "Test User",
  "email": "user@example.com",
  "password": "Password123",
  "role": "candidate"
}

Login Example
{
  "email": "user@example.com",
  "password": "Password123"
}


Response:

{
  "access_token": "<TOKEN>",
  "token_type": "bearer",
  "role": "candidate",
  "user_id": 1
}

🧑‍💼 Jobs (Recruiter Only)
POST /jobs/
GET /jobs/
GET /jobs/{id}
PUT /jobs/{id}
DELETE /jobs/{id}


Example Job Creation:

{
  "title": "Backend Developer",
  "description": "Work on API"
}

📄 Applications
POST /applications/apply/{job_id}
PUT /applications/{id}/stage
GET /applications/my
GET /applications/job/{job_id}
GET /applications/company/{company_id}

Apply to Job

Requires candidate token.

Change Stage

Requires recruiter or hiring_manager token.

Body example:

"Screening"

🧪 Testing the System
✔ Step 1 — Start server + celery worker
✔ Step 2 — Register & login candidate + recruiter
✔ Step 3 — Recruiter creates job
✔ Step 4 — Candidate applies

You should see in Celery:

Received task: send_stage_change_email

✔ Step 5 — Recruiter updates stage

Again Celery logs appear.

✔ Step 6 — Check History Table
SELECT * FROM application_history ORDER BY timestamp DESC;

✔ RBAC Verification

Candidate tries to create job → 403 Forbidden

Candidate tries to change stage → 403 Forbidden

Recruiter edits job from another company → 403 Forbidden

✔ Workflow Verification

Invalid transition → 400 Bad Request

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
                |  Auth • RBAC • Workflow    |
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

                     