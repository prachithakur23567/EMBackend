from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# MARK ATTENDANCE
@router.post("/", response_model=schemas.AttendanceOut, status_code=201)
def mark_attendance(data: schemas.AttendanceCreate, db: Session = Depends(get_db)):

    # Check employee exists
    employee = db.query(models.Employee).filter(
        models.Employee.id == data.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Prevent duplicate attendance for same date
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == data.employee_id,
        models.Attendance.date == data.date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance already marked for this date"
        )

    attendance = models.Attendance(**data.dict())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


# SUMMARY (Present + Absent Count for All Employees)
@router.get("/summary")
def attendance_summary(db: Session = Depends(get_db)):

    result = (
        db.query(
            models.Employee.id,
            models.Employee.full_name,
            models.Employee.department,
            func.sum(
                case(
                    (models.Attendance.status == "Present", 1),
                    else_=0
                )
            ).label("total_present"),
            func.sum(
                case(
                    (models.Attendance.status == "Absent", 1),
                    else_=0
                )
            ).label("total_absent"),
        )
        .outerjoin(
            models.Attendance,
            models.Employee.id == models.Attendance.employee_id
        )
        .group_by(models.Employee.id)
        .all()
    )

    # Convert to JSON serializable format
    summary_list = []
    for row in result:
        summary_list.append({
            "id": row.id,
            "full_name": row.full_name,
            "department": row.department,
            "total_present": row.total_present or 0,
            "total_absent": row.total_absent or 0,
        })

    return summary_list

# Get Full Records
@router.get("/{employee_id}", response_model=list[schemas.AttendanceOut])
def get_attendance(employee_id: int, db: Session = Depends(get_db)):

    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id
    ).all()