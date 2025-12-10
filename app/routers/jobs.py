from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate, JobOut
from app.core.security import require_role

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# -------------------------
# CREATE JOB (RECRUITER)
# -------------------------
@router.post("/", response_model=JobOut)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter"))
):
    job = Job(
        title=job_data.title,
        description=job_data.description,
        company_id=job_data.company_id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# -------------------------
# LIST ALL JOBS (PUBLIC)
# -------------------------
@router.get("/", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.status == "open").all()
    return jobs


# -------------------------
# GET SINGLE JOB DETAILS
# -------------------------
@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}")
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job



# -------------------------
# DELETE JOB (RECRUITER)
# -------------------------
@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("recruiter"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
