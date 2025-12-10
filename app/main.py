from app.models.application_history import ApplicationHistory
from app.models.application import Application
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models.user import User
from app.models.company import Company
from app.models.job import Job   # ✅ JOB MODEL ADDED

from app.routers import auth, company, jobs  # ✅ JOB ROUTER ADDED
from app.core.security import get_current_user
from app.core.rbac import require_role

app = FastAPI(title="ATS Job Application API")

# ✅ CREATE ALL DATABASE TABLES
Base.metadata.create_all(bind=engine)

# ✅ REGISTER ALL ROUTERS
app.include_router(auth.router)
app.include_router(company.router)
app.include_router(jobs.router)   # ✅ IMPORTANT

# ✅ ROOT TEST
@app.get("/")
def root():
    return {"message": "ATS API is running successfully"}

# ✅ AUTH TEST
@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": current_user.id,
        "role": current_user.role
    }

# ✅ ROLE TESTS
@app.get("/candidate-only")
def candidate_only(user: User = Depends(require_role("candidate"))):
    return {"message": "Hello Candidate"}

@app.get("/recruiter-only")
def recruiter_only(user: User = Depends(require_role("recruiter"))):
    return {"message": "Hello Recruiter"}

from app.routers import applications
app.include_router(applications.router)
