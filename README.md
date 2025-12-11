# 🚀 ATS Job Application Tracking System (Backend)

A complete Applicant Tracking System (ATS) backend built using **FastAPI**, **PostgreSQL**, **Celery**, and **Redis**, implementing:

✔ Workflow State Machine  
✔ Role-Based Access Control (RBAC)  
✔ Email Notification System (Async using Celery)  
✔ Multi-tenant architecture (Companies, Recruiters, Hiring Managers)  
✔ Job CRUD  
✔ Application management with history tracking  

This project fulfills the requirements of the **Partnr GPP: ATS Workflow Backend** task.

---

# 📁 Project Structure

app/
├── core/ → security, rbac, workflow logic
├── models/ → database models
├── routers/ → API endpoints
├── schemas/ → request/response schemas
├── tasks/ → async email tasks
├── database.py → DB session + Base
├── main.py → FastAPI entry point
celery_app.py → Celery worker config
alembic/ → DB migrations

yaml
Copy code

---

# 🧰 Tech Stack

- **FastAPI** – main API framework  
- **PostgreSQL** – relational database  
- **SQLAlchemy + Alembic** – ORM + migrations  
- **Redis** – Celery message broker  
- **Celery** – async background job processing  
- **JWT Authentication** – secure login  
- **Passlib (bcrypt)** – password hashing  

---

# ⚙️ Installation

## 1️⃣ Clone repo
git clone https://github.com/prasad5682/ats-job-tracking-system
cd ats-job-tracking-system

shell
Copy code

## 2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate # Windows

shell
Copy code

## 3️⃣ Install dependencies
pip install -r requirements.txt

yaml
Copy code

---

# 🗄️ Database Setup

### Update your `.env` file:
DATABASE_URL=postgresql://postgres:password@localhost:5432/atsdb

sql
Copy code

### Create database:
```sql
CREATE DATABASE atsdb;
Run migrations:
bash
Copy code
alembic upgrade head
▶️ Run the FastAPI Server
lua
Copy code
uvicorn app.main:app --reload
API Docs available at:

👉 http://127.0.0.1:8000/docs
👉 http://127.0.0.1:8000/redoc

📨 Celery Worker (Async Email Notifications)
Start Redis:

pgsql
Copy code
redis-server
Start Celery worker:

nginx
Copy code
celery -A celery_app.celery_app worker --loglevel=info
Emails are sent on:

✔ Application submitted
✔ Application stage updated
✔ Recruiter receives new application alert

🔐 Roles & Permissions (RBAC)
Role	Permissions
Candidate	Apply to jobs, View own applications
Recruiter	Create/Update/Delete jobs, View all company applications
Hiring Manager	View all applications of company
Admin (optional)	Full access

RBAC implemented via:

less
Copy code
Depends(require_role("role1", "role2"))
🔄 Workflow State Machine
Valid Flow:
nginx
Copy code
Applied → Screening → Interview → Offer → Hired
Reject allowed from ANY stage:
nginx
Copy code
Applied → Rejected  
Screening → Rejected  
Interview → Rejected  
Offer → Rejected  
Invalid transitions are blocked automatically.

📮 Application History Logging
Every stage change creates a record:

sql
Copy code
application_id  
old_stage  
new_stage  
changed_by (user id)  
timestamp  
This ensures full audit trail.

🧪 API Endpoints Overview
🔐 Authentication
bash
Copy code
POST /auth/register
POST /auth/login
🧑‍💼 Jobs (Recruiter Only)
bash
Copy code
POST /jobs/
GET /jobs/
GET /jobs/{id}
PUT /jobs/{id}
DELETE /jobs/{id}
📄 Applications
bash
Copy code
POST /applications/apply/{job_id}            (candidate)
PUT /applications/{id}/stage                 (recruiter)
GET /applications/my                         (candidate)
GET /applications/job/{job_id}               (recruiter)
GET /applications/company/{company_id}       (hiring manager)
🧪 Testing with FastAPI Docs
Visit:

👉 http://127.0.0.1:8000/docs

You can test every endpoint with JWT tokens.

📝 Environment Variables
See .env.example


Architecture Overview
                   +----------------------+
                   |      PostgreSQL      |
                   |  Users, Jobs, Apps   |
                   +----------+-----------+
                              |
                              |
                     SQLAlchemy ORM
                              |
                +-------------+--------------+
                |      FastAPI Backend       |
                |-----------------------------|
                | Auth (JWT)                  |
                | RBAC                        |
                | Workflow Engine             |
                | REST API Endpoints          |
                +-------------+--------------+
                              |
               (Sends email tasks to queue)
                              |
                         Redis Queue
                              |
                     +--------+--------+
                     |    Celery Worker |
                     | Processes email  |
                     | sends via SMTP   |
                     +------------------+
                     