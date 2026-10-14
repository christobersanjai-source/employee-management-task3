from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

class DepartmentRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class RoleRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    department_id: Optional[int] = Field(default=None, ge=1)
    manager_id: Optional[int] = Field(default=None, ge=1)
    role_ids: list[int] = Field(default_factory=list)
    joining_date: Optional[date] = None

    @field_validator("full_name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("full_name must not be empty")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()

    @field_validator("role_ids")
    @classmethod
    def unique_role_ids(cls, value: list[int]) -> list[int]:
        if any(item < 1 for item in value):
            raise ValueError("role_ids must contain positive integers")
        if len(value) != len(set(value)):
            raise ValueError("role_ids must not contain duplicates")
        return value

    @model_validator(mode="after")
    def joining_date_not_future(self):
        if self.joining_date and self.joining_date > date.today():
            raise ValueError("joining_date cannot be in the future")
        return self

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    department_id: Optional[int] = Field(default=None, ge=1)
    manager_id: Optional[int] = Field(default=None, ge=1)
    role_ids: Optional[list[int]] = None
    joining_date: Optional[date] = None

    @field_validator("full_name")
    @classmethod
    def name_not_blank(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("full_name must not be empty")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return str(value).lower() if value is not None else value

    @model_validator(mode="after")
    def joining_date_not_future(self):
        if self.joining_date and self.joining_date > date.today():
            raise ValueError("joining_date cannot be in the future")
        return self

class EmployeeRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    role_ids: list[int] = Field(default_factory=list)
    joining_date: Optional[date] = None
    model_config = ConfigDict(from_attributes=True)

class EmployeePage(BaseModel):
    items: list[EmployeeRead]
    total: int
    page: int
    size: int
