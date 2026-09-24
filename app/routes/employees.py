from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging_config import get_logger
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import (
    create_employee,
    delete_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
)

router = APIRouter(prefix="/employees", tags=["Employees"])
logger = get_logger(__name__)


@router.get("/", response_model=list[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    employees = get_all_employees(db)
    logger.info("Listed %d employees", len(employees))
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = get_employee_by_id(db, employee_id)
    if employee is None:
        logger.warning("Employee %s not found", employee_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def add_employee(employee_data: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        employee = create_employee(db, employee_data)
        logger.info("Employee created id=%s email=%s", employee.id, employee.email)
        return employee
    except IntegrityError:
        logger.warning("Duplicate email on create: %s", employee_data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email already exists",
        )


@router.put("/{employee_id}", response_model=EmployeeResponse)
def edit_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    try:
        employee = update_employee(db, employee_id, employee_data)
    except IntegrityError:
        logger.warning("Duplicate email on update for id=%s", employee_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email already exists",
        )

    if employee is None:
        logger.warning("Employee %s not found for update", employee_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    logger.info("Employee updated id=%s", employee_id)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_employee(employee_id: int, db: Session = Depends(get_db)):
    if not delete_employee(db, employee_id):
        logger.warning("Employee %s not found for delete", employee_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    logger.info("Employee deleted id=%s", employee_id)
