from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.application_history import ApplicationHistory
from app.models.job import Job
from app.models.user import User
from app.core.workflow import is_valid_transition
from app.core.rbac import require_role
from app.core.email import send_email   # now uses Celery automatically
from app.core.security import get_current_user

router = APIRouter(prefix="/applications", tags=["Applications"])


# ---------------------------------------------------------
# ✅ 1. CANDIDATE APPLIES TO A JOB
# ---------------------------------------------------------
@router.post("/apply/{job_id}")
def apply_to_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = db.query(Application).filter(
        Application.candidate_id == current_user.id,
        Application.job_id == job_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    application = Application(
        candidate_id=current_user.id,
        job_id=job_id,
        stage="Applied"
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    # History entry
    history = ApplicationHistory(
        application_id=application.id,
        old_stage="Applied",
        new_stage="Applied",
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    # ------------------------------------------------------
    # 📩 CELERY EMAIL — Candidate Notification
    # ------------------------------------------------------
    send_email(
        current_user.email,
        "Application Submitted",
        f"You successfully applied for {job.title}"
    )

    # ------------------------------------------------------
    # 📩 CELERY EMAIL — Recruiter Notification (All recruiters)
    # ------------------------------------------------------
    recruiters = db.query(User).filter(
        User.role == "recruiter",
        User.company_id == job.company_id
    ).all()

    for r in recruiters:
        send_email(
            r.email,
            "New Application Received",
            f"{current_user.full_name} applied for your job: {job.title}"
        )

    return {
        "message": "Application submitted successfully",
        "application_id": application.id
    }


# ---------------------------------------------------------
# ✅ 2. RECRUITER CHANGES STAGE
# ---------------------------------------------------------
@router.put("/{application_id}/stage")
def change_stage(
    application_id: int,
    new_stage: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    current_stage = application.stage

    # Validate workflow
    if not is_valid_transition(current_stage, new_stage):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_stage} → {new_stage}"
        )

    application.stage = new_stage
    db.commit()

    # Save stage history
    history = ApplicationHistory(
        application_id=application.id,
        old_stage=current_stage,
        new_stage=new_stage,
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    # ------------------------------------------------------
    # 📩 CELERY EMAIL — Candidate status update
    # ------------------------------------------------------
    send_email(
        application.candidate.email,
        "Application Status Updated",
        f"Your application moved from {current_stage} → {new_stage}"
    )

    return {
        "message": "Stage updated successfully",
        "application_id": application.id,
        "old_stage": current_stage,
        "new_stage": new_stage
    }


# ---------------------------------------------------------
# ✅ 3. CANDIDATE VIEWS THEIR OWN APPLICATIONS
# ---------------------------------------------------------
@router.get("/my")
def my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    return db.query(Application).filter(
        Application.candidate_id == current_user.id
    ).all()


# ---------------------------------------------------------
# ✅ 4. RECRUITER VIEWS APPLICATIONS FOR A JOB (filter optional)
# ---------------------------------------------------------
@router.get("/job/{job_id}")
def job_applications(
    job_id: int,
    stage: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    query = db.query(Application).filter(Application.job_id == job_id)

    if stage:
        query = query.filter(Application.stage == stage)

    return query.all()


# ---------------------------------------------------------
# ✅ 5. VIEW APPLICATION BY ID
# ---------------------------------------------------------
@router.get("/{application_id}")
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Candidate can only view their own application
    if current_user.role == "candidate" and application.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return application


# ---------------------------------------------------------
# ✅ 6. HIRING MANAGER – View all company applications
# ---------------------------------------------------------
@router.get("/company/{company_id}")
def company_applications(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hiring_manager"))
):
    return (
        db.query(Application)
        .join(Job)
        .filter(Job.company_id == company_id)
        .all()
    )
