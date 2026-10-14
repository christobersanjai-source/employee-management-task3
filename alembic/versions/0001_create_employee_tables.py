"""create employee, department, role and employee_roles tables

Revision ID: 0001_employee_tables
Revises:
Create Date: 2026-10-13
"""
from alembic import op
import sqlalchemy as sa
revision = "0001_employee_tables"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("departments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False, unique=True))
    op.create_index("ix_departments_name", "departments", ["name"])
    op.create_table("roles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(80), nullable=False, unique=True))
    op.create_index("ix_roles_name", "roles", ["name"])
    op.create_table("employees", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("full_name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True), sa.Column("manager_id", sa.Integer(), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True), sa.Column("joining_date", sa.Date(), nullable=True), sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("ix_employees_full_name", "employees", ["full_name"])
    op.create_index("ix_employees_email", "employees", ["email"])
    op.create_index("ix_employees_department_id", "employees", ["department_id"])
    op.create_index("ix_employees_manager_id", "employees", ["manager_id"])
    op.create_index("ix_employees_is_deleted", "employees", ["is_deleted"])
    op.create_table("employee_roles", sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True), sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True))

def downgrade():
    op.drop_table("employee_roles")
    for name in ["ix_employees_is_deleted", "ix_employees_manager_id", "ix_employees_department_id", "ix_employees_email", "ix_employees_full_name"]: op.drop_index(name, table_name="employees")
    op.drop_table("employees")
    op.drop_index("ix_roles_name", table_name="roles"); op.drop_table("roles")
    op.drop_index("ix_departments_name", table_name="departments"); op.drop_table("departments")
