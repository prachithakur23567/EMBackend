from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/employees", tags=["Employees"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.delete("/{employee_id}", status_code=200)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):

    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}


@router.post("/", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):

    # Duplicate employee_id check
    existing = db.query(models.Employee).filter(
        models.Employee.employee_id == employee.employee_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Employee ID already exists"
        )

    new_employee = models.Employee(**employee.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@router.get("/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()