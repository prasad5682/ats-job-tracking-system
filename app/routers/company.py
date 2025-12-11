from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.user import User
from app.core.security import get_current_user
from app.core.rbac import require_role

router = APIRouter(prefix="/company", tags=["Company"])


# ---------------------------------------------------------
# ✅ 1. CREATE COMPANY — Recruiter Only
# ---------------------------------------------------------
@router.post("/")
def create_company(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    name = data.get("name")
    description = data.get("description")

    if not name:
        raise HTTPException(status_code=400, detail="Company name is required")

    # Check if company already exists
    existing = db.query(Company).filter(Company.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")

    company = Company(
        name=name,
        description=description
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    # Assign recruiter to this company (useful for ATS workflow)
    current_user.company_id = company.id
    db.commit()

    return {
        "message": "Company created successfully",
        "company_id": company.id
    }


# ---------------------------------------------------------
# ✅ 2. UPDATE COMPANY — Recruiter Only (same company)
# ---------------------------------------------------------
@router.put("/{company_id}")
def update_company(
    company_id: int,
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Recruiter must belong to same company
    if company.id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this company")

    if "name" in updates:
        company.name = updates["name"]

    if "description" in updates:
        company.description = updates["description"]

    db.commit()
    db.refresh(company)

    return {
        "message": "Company updated successfully",
        "company": company
    }


# ---------------------------------------------------------
# ✅ 3. DELETE COMPANY — Recruiter Only (same company)
# ---------------------------------------------------------
@router.delete("/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this company")

    db.delete(company)
    db.commit()

    return {"message": "Company deleted successfully"}


# ---------------------------------------------------------
# ✅ 4. GET COMPANY BY ID — Everyone Can View
# ---------------------------------------------------------
@router.get("/{company_id}")
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


# ---------------------------------------------------------
# ✅ 5. LIST ALL COMPANIES — Anyone Can View
# ---------------------------------------------------------
@router.get("/")
def list_companies(
    db: Session = Depends(get_db)
):
    return db.query(Company).all()
