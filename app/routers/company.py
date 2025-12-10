from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.company import Company
from app.core.security import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/")
def create_company(
    name: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ["recruiter", "hiring_manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    company = Company(name=name)
    db.add(company)
    db.commit()
    db.refresh(company)

    return company
