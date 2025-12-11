from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.models.user import User
from app.core.rbac import require_role
from app.core.security import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ---------------------------------------------------------
# ✅ 1. CREATE JOB — Recruiter Only
# ---------------------------------------------------------
@router.post("/")
def create_job(
    job_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    # Recruiter must belong to a company
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Recruiter is not assigned to any company")

    job = Job(
        title=job_data.get("title"),
        description=job_data.get("description"),
        company_id=current_user.company_id,
        status=job_data.get("status", "open").lower()
    )

    if job.status not in ["open", "closed"]:
        raise HTTPException(status_code=400, detail="Status must be 'open' or 'closed'")

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "message": "Job created successfully",
        "job_id": job.id
    }


# ---------------------------------------------------------
# ✅ 2. UPDATE JOB — Recruiter Only (same company)
# ---------------------------------------------------------
@router.put("/{job_id}")
def update_job(
    job_id: int,
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Recruiter must belong to same company
    if job.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this job")

    # Update fields
    if "title" in updates:
        job.title = updates["title"]
    if "description" in updates:
        job.description = updates["description"]
    if "status" in updates:
        status = updates["status"].lower()
        if status not in ["open", "closed"]:
            raise HTTPException(status_code=400, detail="Status must be 'open' or 'closed'")
        job.status = status

    db.commit()
    db.refresh(job)

    return {
        "message": "Job updated successfully",
        "updated_job": job
    }


# ---------------------------------------------------------
# ✅ 3. DELETE JOB — Recruiter Only (same company)
# ---------------------------------------------------------
@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this job")

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}


# ---------------------------------------------------------
# ✅ 4. GET JOB BY ID — Everyone Can View
# ---------------------------------------------------------
@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


# ---------------------------------------------------------
# ✅ 5. LIST ALL JOBS — Everyone Can View
# ---------------------------------------------------------
@router.get("/")
def list_jobs(
    status: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Job)

    if status:
        status = status.lower()
        if status not in ["open", "closed"]:
            raise HTTPException(status_code=400, detail="Status must be 'open' or 'closed'")
        query = query.filter(Job.status == status)

    return query.all()


# ---------------------------------------------------------
# ✅ 6. HIRING MANAGER — View all jobs in their company
# ---------------------------------------------------------
@router.get("/company/all")
def company_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hiring_manager"))
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Hiring manager is not assigned to any company")

    return db.query(Job).filter(Job.company_id == current_user.company_id).all()
