from sqlalchemy import String, ForeignKey, Table, Column, Index, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

employee_roles = Table(
    "employee_roles", Base.metadata,
    Column("employee_id", ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (Index("ix_employees_department_id", "department_id"), Index("ix_employees_manager_id", "manager_id"))
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    joining_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    department: Mapped["Department | None"] = relationship(back_populates="employees")
    manager: Mapped["Employee | None"] = relationship(remote_side="Employee.id", back_populates="direct_reports")
    direct_reports: Mapped[list["Employee"]] = relationship(back_populates="manager")
    roles: Mapped[list["Role"]] = relationship(secondary="employee_roles", back_populates="employees")
