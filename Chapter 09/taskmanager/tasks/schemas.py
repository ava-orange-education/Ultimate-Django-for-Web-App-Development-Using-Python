import datetime

from django.contrib.auth.models import User
from ninja import Field, FilterSchema, ModelSchema, Schema
from pydantic import model_validator
from tasks.enums import TaskStatus
from tasks.models import Task


class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ["id", "username"]


class TaskSchemaIn(Schema):
    class Config:
        description = "Schema for creating a new task"
        model = Task
        model_fields = ["title", "description"]
        model_fields_optional = ["status"]


class CreateSchemaOut(Schema):
    id: int = Field(..., example=1)

    class Config:
        description = "Schema for the created object output"


class TaskSchemaOut(ModelSchema):
    owner: UserSchema | None = Field(None)

    class Config:
        model = Task
        model_fields = ["id", "title", "description", "status"]


class PathDate(Schema):
    year: int = Field(..., ge=1)  # Year must be greater than or equal to 1.
    month: int = Field(..., ge=1, le=12)  # Month must be between 1 and 12.
    day: int = Field(..., ge=1, le=31)  # Day must be between 1 and 31.

    @model_validator(mode="after")
    def validate_date(self) -> "PathDate":
        try:
            return datetime.date(self.year, self.month, self.day)
        except ValueError:
            raise ValueError(
                f"The date {self.year}-{self.month}-{self.day} is not valid."
            )


class TaskFilterSchema(FilterSchema):
    title: str | None
    status: TaskStatus | None
