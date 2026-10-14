from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from app.models import Employee, Department, Role
from app.schemas import EmployeeCreate, EmployeeUpdate

def _get_related(db: Session, department_id, manager_id, role_ids):
    if department_id is not None and db.get(Department, department_id) is None:
        raise HTTPException(status_code=404, detail={"error": "department_not_found", "message": "Department not found"})
    if manager_id is not None:
        if db.get(Employee, manager_id) is None:
            raise HTTPException(status_code=404, detail={"error": "manager_not_found", "message": "Manager not found"})
    roles = []
    for role_id in role_ids or []:
        role = db.get(Role, role_id)
        if role is None:
            raise HTTPException(status_code=404, detail={"error": "role_not_found", "message": f"Role {role_id} not found"})
        roles.append(role)
    return roles

def list_employees(db: Session, page: int, size: int, department: int | None, q: str | None):
    query = db.query(Employee).options(selectinload(Employee.roles)).filter(Employee.is_deleted.is_(False))
    if department is not None:
        query = query.filter(Employee.department_id == department)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Employee.full_name.ilike(term), Employee.email.ilike(term)))
    total = query.count()
    items = query.order_by(Employee.id).offset((page - 1) * size).limit(size).all()
    return {"items": [employee_dict(e) for e in items], "total": total, "page": page, "size": size}

def employee_dict(e):
    return {"id": e.id, "full_name": e.full_name, "email": e.email, "department_id": e.department_id, "manager_id": e.manager_id, "role_ids": [r.id for r in e.roles], "joining_date": e.joining_date}

def create_employee(db: Session, payload: EmployeeCreate):
    roles = _get_related(db, payload.department_id, payload.manager_id, payload.role_ids)
    employee = Employee(full_name=payload.full_name, email=str(payload.email).lower(), department_id=payload.department_id, manager_id=payload.manager_id, joining_date=payload.joining_date, roles=roles)
    db.add(employee)
    try:
        db.commit(); db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": "conflict", "message": "Email already exists or database constraint failed"})
    return employee_dict(employee)

def get_employee(db: Session, employee_id: int):
    employee = db.query(Employee).options(selectinload(Employee.roles)).filter(Employee.id == employee_id, Employee.is_deleted.is_(False)).first()
    if not employee:
        raise HTTPException(status_code=404, detail={"error": "employee_not_found", "message": "Employee not found"})
    return employee

def update_employee(db: Session, employee_id: int, payload: EmployeeUpdate):
    employee = get_employee(db, employee_id)
    data = payload.model_dump(exclude_unset=True)
    roles = None
    if "role_ids" in data and data["role_ids"] is not None:
        roles = _get_related(db, employee.department_id, employee.manager_id, data["role_ids"])
    _get_related(db, data.get("department_id", employee.department_id), data.get("manager_id", employee.manager_id), [])
    if data.get("manager_id") == employee_id:
        raise HTTPException(status_code=400, detail={"error": "invalid_manager", "message": "An employee cannot be their own manager"})
    if "role_ids" in data:
        data.pop("role_ids")
        if roles is not None: employee.roles = roles
    for key, value in data.items():
        if key == "email" and value is not None: value = str(value).lower()
        setattr(employee, key, value)
    try:
        db.commit(); db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": "conflict", "message": "Email already exists or database constraint failed"})
    return employee_dict(employee)

def soft_delete_employee(db: Session, employee_id: int):
    employee = get_employee(db, employee_id)
    employee.is_deleted = True
    db.commit()
    return {"message": "Employee soft-deleted", "id": employee_id}

def department_employees(db: Session, department_id: int):
    if db.get(Department, department_id) is None:
        raise HTTPException(status_code=404, detail={"error": "department_not_found", "message": "Department not found"})
    rows = db.query(Employee).options(selectinload(Employee.roles)).filter(Employee.department_id == department_id, Employee.is_deleted.is_(False)).order_by(Employee.id).all()
    return [employee_dict(e) for e in rows]

def direct_reports(db: Session, employee_id: int):
    get_employee(db, employee_id)
    rows = db.query(Employee).options(selectinload(Employee.roles)).filter(Employee.manager_id == employee_id, Employee.is_deleted.is_(False)).order_by(Employee.id).all()
    return [employee_dict(e) for e in rows]
