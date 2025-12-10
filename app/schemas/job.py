from pydantic import BaseModel
from typing import Optional


class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    company_id: int


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    company_id: Optional[int] = None


class JobOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    company_id: int

    class Config:
        orm_mode = True
