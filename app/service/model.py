"""
model.py

This module contains domain models used across the application. These are plain data
structures that represent user input and service-level representations of the entities
in the system, detached from the persistence layer.

Classes:
    User:
        Represents a user with personal and contact information.

    Project:
        Represents a project with metadata including dates, status, and assigned user.

    Task:
        Represents a task associated with a project, including status and scheduling.

    Comment:
        Represents a user comment associated with a specific task.

Dependencies:
    - datetime, dataclasses
    - ProjectStatusEnum (from db.entity)
"""

from dataclasses import dataclass
from datetime import datetime, date
from app.db.entity import ProjectStatusEnum

@dataclass
class User:
    """Represents a user entity in the system."""
    name: str
    surname: str
    email: str

@dataclass
class Project:
    """Represents a project entity with status, dates, and ownership."""
    name: str
    description: str
    start_date: date
    end_date: date | None = None
    status: ProjectStatusEnum = ProjectStatusEnum.PLANNED
    user_id: int | None = None

@dataclass
class Task:
    """Represents a task within a project with scheduling and status details."""
    title: str
    description: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    project_id: int | None = None

@dataclass
class Comment:
    """Represents a user comment associated with a specific task."""
    content: str
    creation_date: str
    task_id: int
