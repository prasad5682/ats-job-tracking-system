from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.application_history import ApplicationHistory
from app.models.job import Job
from app.models.user import User

from app.core.workflow import is_valid_transition, get_allowed_transitions, VALID_STAGES
from app.core.rbac import require_role
from app.tasks.email_tasks import send_stage_change_email, notify_recruiter_new_application
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

    # Prevent duplicate applications
    existing = (
        db.query(Application)
        .filter(
            Application.candidate_id == current_user.id,
            Application.job_id == job_id
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    # Create new application
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
        old_stage=None,
        new_stage="Applied",
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    # 📩 Email to candidate (Async)
    send_stage_change_email.delay(
        current_user.email,
        job.title,
        "Applied"
    )

    # 📩 Email to all company recruiters (Async)
    recruiters = db.query(User).filter(
        User.role == "recruiter",
        User.company_id == job.company_id
    ).all()

    for r in recruiters:
        notify_recruiter_new_application.delay(
            r.email,
            job.title,
            current_user.email
        )

    return {
        "message": "Application submitted successfully",
        "application_id": application.id
    }


# ---------------------------------------------------------
# ✅ 2. RECRUITER OR HIRING MANAGER CHANGES STAGE
# ---------------------------------------------------------
@router.put("/{application_id}/stage")
def change_stage(
    application_id: int,
    new_stage: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "hiring_manager"))
):
    new_stage = new_stage.strip().title()  # Normalize stage input

    if new_stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {new_stage}")

    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    current_stage = application.stage

    # Validate workflow transition
    if not is_valid_transition(current_stage, new_stage):
        allowed = get_allowed_transitions(current_stage)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition {current_stage} → {new_stage}. Allowed: {allowed}"
        )

    # Update stage
    application.stage = new_stage
    db.commit()
    db.refresh(application)

    # Save history entry
    history = ApplicationHistory(
        application_id=application.id,
        old_stage=current_stage,
        new_stage=new_stage,
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    # 📩 Notify candidate asynchronously
    send_stage_change_email.delay(
        application.candidate.email,
        application.job.title,
        new_stage
    )

    return {
        "message": "Stage updated successfully",
        "application_id": application.id,
        "old_stage": current_stage,
        "new_stage": new_stage
    }


# ---------------------------------------------------------
# ✅ 3. Candidate views their own applications
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
# ✅ 4. Recruiter views applications for a job
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
        stage = stage.strip().title()
        query = query.filter(Application.stage == stage)

    return query.all()


# ---------------------------------------------------------
# ✅ 5. View application by ID
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

    # Candidate can only see their own application
    if current_user.role == "candidate" and application.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return application


# ---------------------------------------------------------
# ✅ 6. Hiring manager views all company applications
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
