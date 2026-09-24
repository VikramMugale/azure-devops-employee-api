from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def get_all_employees(db: Session) -> list[Employee]:
    statement = select(Employee).order_by(Employee.id)
    return list(db.scalars(statement).all())


def get_employee_by_id(db: Session, employee_id: int) -> Employee | None:
    return db.get(Employee, employee_id)


def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
    employee = Employee(**employee_data.model_dump())
    db.add(employee)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(employee)
    return employee


def update_employee(
    db: Session,
    employee_id: int,
    employee_data: EmployeeUpdate,
) -> Employee | None:
    employee = db.get(Employee, employee_id)
    if employee is None:
        return None

    for field, value in employee_data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee_id: int) -> bool:
    employee = db.get(Employee, employee_id)
    if employee is None:
        return False

    db.delete(employee)
    db.commit()
    return True
