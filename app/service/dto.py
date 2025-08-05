from dataclasses import dataclass, field
from typing import Self
from datetime import date, datetime
from app.db.entity import ProjectStatusEnum, TaskStatusEnum




@dataclass
class CreateUserDto:
    name: str
    surname: str
    email: str

@dataclass
class CreateProjectDto:
    name: str
    description: str
    start_date: date
    end_date: date
    status: ProjectStatusEnum
    user_id: int

@dataclass
class CreateTaskDto:
    title: str
    description: str
    start_date: date
    end_date: date
    status: TaskStatusEnum
    project_id: int

@dataclass
class CreateCommentDto:
    content: str
    creation_date: str
    task_id: int

@dataclass
class CreateTaskHistoryDto:
    change_description: str
    change_date: str
    task_id: int


