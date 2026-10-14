import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.db.base import Base
from app.models import Employee, Department, Role

@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_employee_department_manager_and_roles(db):
    dept = Department(name="IT")
    role = Role(name="Developer")
    db.add_all([dept, role])
    db.flush()
    manager = Employee(full_name="Arun", email="arun@example.com", department=dept, roles=[role])
    db.add(manager)
    db.flush()
    worker = Employee(full_name="Kumar", email="kumar@example.com", department=dept, manager=manager, roles=[role])
    db.add(worker)
    db.commit()
    assert worker.department.name == "IT"
    assert worker.manager.email == "arun@example.com"
    assert worker in manager.direct_reports
    assert worker.roles[0].name == "Developer"

def test_duplicate_email_is_rejected(db):
    db.add(Employee(full_name="A", email="same@example.com"))
    db.commit()
    db.add(Employee(full_name="B", email="same@example.com"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
