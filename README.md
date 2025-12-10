Job Application Tracking System (ATS)

A complete backend system for managing job applications with:

Workflow state machine

Role-Based Access Control (RBAC)

Asynchronous email notifications (Celery + Redis)

Audit logs

Multi-tenant company support

Fully authenticated JWT-protected API

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

This project is a backend system for a Job Application Tracking System (ATS) built using FastAPI.
It supports a complete hiring workflow, role-based access permissions, and background email notifications.

The goal of this project is to simulate a real-world recruitment system where companies can post jobs, candidates can apply, recruiters can manage applications, and hiring managers can review the progress.

 What This System Can Do
👤 User Roles

The system supports three user roles:

Candidate – applies for jobs, views own applications

Recruiter – manages job postings and application stages

Hiring Manager – reviews all applications for their company

Each role has specific permissions, enforced through RBAC.

 Main Features
 Authentication

Register and login using JWT

Password hashing for security

 Job Management

Recruiters can:

Create a job

Update job details

Delete a job

View all jobs

Anyone can view open jobs.

 Application Management
Candidate:

Apply for any job once

View all applications submitted

Recruiter:

View applications for jobs in their company

Filter applications by stage

Change the application stage (Screening, Interview, Offer, Hired, Rejected)

Hiring Manager:

View all applications under their company

 Workflow / Stage System

Each application moves through a predefined workflow:

Applied → Screening → Interview → Offer → Hired


At any time, the application can also move to:

Rejected


Invalid transitions (like jumping from Applied → Offer) are blocked.

 Email Notifications (Asynchronous)

Emails are sent for important events:

When a candidate applies to a job

When a recruiter updates the application stage

All recruiters in the same company are notified when a new application arrives

Emails are sent using:

Celery (background task worker)

Redis (message broker)

This ensures the API stays fast and responsive.

🗂 Project Structure
app/
 ├── core/          # RBAC, email logic, workflow validation, security
 ├── models/        # SQLAlchemy models (User, Job, Application, etc.)
 ├── routers/       # All API route files
 ├── schemas/       # Pydantic schemas for validation
 ├── database.py
 ├── main.py
celery_app.py        # Celery worker configuration
alembic/             # Database migrations
requirements.txt

 How to Run the Project
 Install dependencies
pip install -r requirements.txt

Start Redis (message broker)
redis-server

 Start Celery Worker
celery -A celery_app.celery_app worker --loglevel=info

 Run the FastAPI Server
uvicorn app.main:app --reload


Open API docs:

http://127.0.0.1:8000/docs

 Testing the System

Here are simple ways to test your features:

✔ Candidate applying for a job

Send a POST request:

/applications/apply/{job_id}  

✔ Recruiter updating stage
/applications/{application_id}/stage?new_stage=Interview

✔ View candidate’s applications
/applications/my

✔ View applications per job (recruiter)
/applications/job/{job_id}

✔ View full company applications (hiring manager)
/applications/company/{company_id}

 What This Project Demonstrates

This ATS project shows real backend engineering abilities:

Designing relational models with SQLAlchemy

Implementing workflows and validation rules

Using JWT for secure authentication

Building modular, maintainable FastAPI apps

Using Celery workers for non-blocking background tasks

Implementing RBAC for multi-role systems

Creating audit logs for transparency

 Conclusion

This backend system implements all core requirements of an Applicant Tracking System and mirrors real-world hiring workflows. It is scalable, cleanly structured, and demonstrates strong backend development and system design principles.
Login


