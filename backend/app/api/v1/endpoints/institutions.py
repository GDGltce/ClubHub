"""
Institution endpoints (colleges + departments)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.institution import College, Department
from app.schemas.institution import CollegeCreate, CollegeOut, DepartmentCreate, DepartmentOut
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/institutions", tags=["Institutions"])


# --- Colleges ---
@router.get("/colleges", response_model=List[CollegeOut])
def list_colleges(db: Session = Depends(get_db)):
    return db.query(College).all()


@router.post("/colleges", response_model=CollegeOut, status_code=201)
def create_college(body: CollegeCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    college = College(**body.model_dump())
    db.add(college)
    db.commit()
    db.refresh(college)
    return college


@router.get("/colleges/{college_id}", response_model=CollegeOut)
def get_college(college_id: str, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        raise HTTPException(404, "College not found")
    return college


# --- Departments ---
@router.get("/colleges/{college_id}/departments", response_model=List[DepartmentOut])
def list_departments(college_id: str, db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.college_id == college_id).all()


@router.post("/colleges/{college_id}/departments", response_model=DepartmentOut, status_code=201)
def create_department(
    college_id: str, body: DepartmentCreate,
    db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    dept = Department(**{**body.model_dump(), "college_id": college_id})
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept
