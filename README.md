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
               
               ## Run locally

1. Create and activate virtual environment
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Copy .env.example to .env and edit values
# Windows
copy .env.example .env
# Mac / Linux
cp .env.example .env
# Then open .env and set correct DATABASE_URL, REDIS_URL, SECRET_KEY, SENDGRID_API_KEY, etc.

4. Start Redis
# If installed locally:
redis-server
# Or using Docker:
docker run -d --name redis -p 6379:6379 redis

5. Start PostgreSQL (if using Docker):
docker run -d --name pg -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=atsdb -p 5432:5432 postgres

6. Run database migrations (alembic)
alembic upgrade head

7. Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

8. Start Celery worker (in another terminal)
# Use this exact command (adjust module path if needed)
celery -A celery_app.celery worker --loglevel=info

## Environment

1. Copy .env.example to .env:
# Windows
copy .env.example .env
# Mac / Linux
cp .env.example .env

2. Update values in .env:
- DATABASE_URL (postgres connection)
- REDIS_URL (redis URL)
- SECRET_KEY (random string used for JWT)
- ACCESS_TOKEN_EXPIRE_MINUTES (e.g. 60)
- EMAIL_FROM and SENDGRID_API_KEY (or other email provider credentials)

Do NOT commit `.env` to git (it's in .gitignore).

## API Examples

Register (candidate)
POST http://127.0.0.1:8000/auth/register
Headers: Content-Type: application/json
Body:
{
  "full_name": "Test Candidate",
  "email": "candidate@example.com",
  "password": "Password123",
  "role": "candidate"
}

Login
POST http://127.0.0.1:8000/auth/login
Headers: Content-Type: application/json
Body:
{
  "email": "candidate@example.com",
  "password": "Password123"
}
Response:
{
  "access_token": "<TOKEN>",
  "token_type": "bearer",
  "role": "candidate",
  "user_id": 1
}
# Use access_token in Authorization header: "Authorization: Bearer <TOKEN>"

Create Company (recruiter)
# First register and login a recruiter with role "recruiter" (use email/password)
POST /company/
Headers: Authorization: Bearer <RECRUITER_TOKEN>
Body:
{
  "name": "Acme Co",
  "description": "Company description"
}

Create Job (recruiter)
POST http://127.0.0.1:8000/jobs/
Headers:
  Authorization: Bearer <RECRUITER_TOKEN>
  Content-Type: application/json
Body:
{
  "title": "Backend Developer",
  "description": "Work on API"
}

Apply to Job (candidate)
POST http://127.0.0.1:8000/applications/apply/{job_id}
Headers: Authorization: Bearer <CANDIDATE_TOKEN>
(no body required)

Change Stage (recruiter or hiring_manager)
PUT http://127.0.0.1:8000/applications/{application_id}/stage
Headers:
  Authorization: Bearer <RECRUITER_TOKEN>
  Content-Type: application/json
Body:
"Screening"

## Testing & verification

1. Start server and Celery worker (see Run locally).

2. Register candidate and recruiter, login both and save tokens.

3. As recruiter:
   - Create a company (if company creation is required)
   - Create a job and note its job_id

4. As candidate:
   - Apply to that job (POST /applications/apply/{job_id})
   - Check response: application_id returned

5. Celery verification:
   - Watch the Celery worker terminal. When you apply, you should see a task received:
     [INFO/MainProcess] Received task: app.tasks.email_tasks.notify_recruiter_new_application[...]
     and then succeeded lines.
   - When recruiter changes stage, worker should receive send_stage_change_email task.

6. Check ApplicationHistory:
   - Query database:
     SELECT * FROM application_history WHERE application_id = <id> ORDER BY timestamp DESC;
   - You should see entries for application creation and each stage change.

7. RBAC checks:
   - Try to create a job with a candidate token → should return 403.
   - Try to change stage with candidate token → should return 403.
   - Try to modify a job belonging to another company → should return 403.

8. Workflow checks:
   - Try invalid transition (Applied → Offer) -> API should return 400 and allowed transitions list.
