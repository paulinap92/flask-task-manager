"""
task_service.py

This module defines the abstract interface and implementation of task-related services,
integrating task management with history logging.

Classes:
    TaskService (ABC):
        Abstract base class for defining task-related operations.

    TaskServiceImpl:
        Concrete implementation for task creation, status updates,
        deletion, and audit logging.

Methods:
    create_task(create_task_dto: CreateTaskDto) -> Task:
        Creates a new task and logs it in TaskHistory.

    delete_by_id(task_id: int) -> None:
        Deletes a task and logs the deletion.

    change_status(task_id: int, new_status: TaskStatusEnum) -> Task:
        Updates task status and logs the change.

    find_all_tasks() -> list[Task]:
        Returns a list of all tasks.

    find_by_id(task_id: int) -> Task:
        Returns a single task by ID.

    find_by_name(task_id: int) -> Task:
        Finds a task by ID (despite name of method).

Dependencies:
    - TaskRepository, TaskHistoryRepository, ProjectRepository
    - CreateTaskDto, Task, TaskEntity, TaskHistoryEntity
    - CURRENT_TIMEZONE from app.config.timezone
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List

from app.service.model import Task
from app.db.repository import (
    TaskRepository,
    task_repository,
    TaskHistoryRepository,
    task_history_repository,
    ProjectRepository,
    project_repository
)
from app.service.dto import CreateTaskDto
from app.db.entity import TaskEntity, TaskHistoryEntity, TaskStatusEnum
from datetime import datetime
from app.config.current_timezone import CURRENT_TIMEZONE

import logging
logging.basicConfig(level=logging.INFO)


class TaskService(ABC):
    """Abstract interface for task-related operations."""

    @abstractmethod
    def create_task(self, create_task_dto: CreateTaskDto) -> Task:
        """Create a new task and return it."""
        pass

    @abstractmethod
    def delete_by_id(self, task_id: int) -> None:
        """Delete a task by its ID."""
        pass

    @abstractmethod
    def find_all_tasks(self) -> list[Task]:
        """Return all tasks."""
        pass

    @abstractmethod
    def find_by_id(self, task_id: int) -> Task:
        """Return task by ID."""
        pass

    @abstractmethod
    def find_by_name(self, task_id: int) -> Task:
        """Find task by its ID (method name misleading)."""
        pass


@dataclass
class TaskServiceImpl(TaskService):
    """Service layer for task management with automatic history logging.

    Attributes:
        task_repository (TaskRepository): Persistence layer for tasks.
        project_repository (ProjectRepository): Used to verify project existence.
        task_history_repository (TaskHistoryRepository): Persistence for history entries.
    """

    task_repository: TaskRepository
    project_repository: ProjectRepository
    task_history_repository: TaskHistoryRepository

    def create_task(self, create_task_dto: CreateTaskDto) -> Task:
        """Create a task and immediately log it in task history."""
        project = self.project_repository.find_by_id(create_task_dto.project_id)
        if not project:
            raise ValueError(f"Project with ID {create_task_dto.project_id} does not exist.")

        task = TaskEntity(
            title=create_task_dto.title,
            description=create_task_dto.description,
            status=create_task_dto.status,
            start_date=create_task_dto.start_date,
            end_date=create_task_dto.end_date,
            project_id=create_task_dto.project_id
        )
        self.task_repository.save_or_update(task)

        history = TaskHistoryEntity(
            change_description=f"New task '{task.title}' has been created.",
            change_date=datetime.now(CURRENT_TIMEZONE),
            task_id=task.id
        )
        self.task_history_repository.save_or_update(history)

        return task

    def delete_by_id(self, task_id: int) -> None:
        """Delete a task and log the deletion in history."""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist.")

        history = TaskHistoryEntity(
            change_description=f"Task '{task.title}' has been deleted.",
            change_date=datetime.now(CURRENT_TIMEZONE),
            task_id=task.id
        )
        self.task_history_repository.save_or_update(history)
        self.task_repository.delete_by_id(task_id)

    def change_status(self, task_id: int, new_status: TaskStatusEnum) -> Task:
        """Change the status of a task and log the change."""
        task = self.task_repository.find_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist.")

        old_status = task.status
        task.status = new_status
        self.task_repository.save_or_update(task)

        history = TaskHistoryEntity(
            change_description=f"Task '{task.title}' status changed from '{old_status.name}' to '{new_status.name}'.",
            change_date=datetime.now(CURRENT_TIMEZONE),
            task_id=task.id
        )
        self.task_history_repository.save_or_update(history)

        return task

    def find_all_tasks(self) -> list[Task]:
        """Return all tasks."""
        return self.task_repository.find_all()

    def find_by_id(self, task_id: int) -> Task:
        """Find a task by ID."""
        return self.task_repository.find_by_id(task_id)

    def find_by_name(self, task_id: int) -> Task:
        """Find a task by ID (method name misleading)."""
        return self.task_repository.find_by_name(task_id)

    def find_all_filtered_by_status(self, status: TaskStatusEnum) -> list[Task]:
        """Return all tasks."""
        return self.task_repository.find_by_status(status)

    def find_all_sorted_by_date(self, sort_by: str = 'start_date', descending: bool = False)-> list[Task]:
        """Return all tasks sorted by a date field.

        Args:
            sort_by (str): The field to sort by ('start_date' or 'end_date').
            descending (bool): Whether the sorting should be descending.

        Returns:
            List[Task]: Sorted list of tasks.
        """
        if sort_by not in {'start_date', 'end_date'}:
            raise ValueError("Invalid sorting field. Use 'start_date' or 'end_date'.")
        return self.task_repository.find_all_sorted_by_date(sort_by, descending=descending)

