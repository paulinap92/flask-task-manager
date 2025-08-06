"""
project_service.py

This module defines the abstract interface and implementation of project-related services,
providing CRUD operations and project-user associations.

Classes:
    ProjectService (ABC):
        Abstract base class for defining project-related operations.

    ProjectServiceImpl:
        Concrete implementation for creating, deleting, and retrieving projects,
        as well as assigning them to users and sorting/filtering by dates.

Methods:
    create_project(create_project_dto: CreateProjectDto) -> Project:
        Creates a new project and returns it.

    delete_by_id(project_id: int) -> None:
        Deletes a project by ID.

    find_all_projects() -> List[Project]:
        Returns all available projects.

    find_by_id(project_id: int) -> Project:
        Finds a project by its ID.

    find_by_name(project_id: int) -> Project:
        Finds a project by ID (method name misleading).

    assign_project_to_user(user_id: int, project_id: int) -> None:
        Assigns a project to a user.

    find_all_sorted_by_date(sort_by: str = 'start_date', descending: bool = False):
        Returns all projects sorted by date.

    find_all_filtered_by_date(input_date: date, filter_by: str = 'start_date'):
        Returns all projects matching the specified date.

Dependencies:
    - ProjectRepository, ProjectEntity, ProjectStatusEnum
    - CreateProjectDto, Project
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
from datetime import date

from app.service.model import Project
from app.db.repository import ProjectRepository
from app.service.dto import CreateProjectDto
from app.db.entity import ProjectEntity, ProjectStatusEnum

import logging
logging.basicConfig(level=logging.INFO)

class ProjectService(ABC):
    """Abstract interface for project-related operations."""

    @abstractmethod
    def create_project(self, create_project_dto: CreateProjectDto) -> Project:
        """Create a new project and return it."""
        pass

    @abstractmethod
    def delete_by_id(self, project_id: int) -> None:
        """Delete a project by its ID."""
        pass

    @abstractmethod
    def find_all_projects(self) -> List[Project]:
        """Return all projects."""
        pass

    @abstractmethod
    def find_by_id(self, project_id: int) -> Project:
        """Find a project by ID."""
        pass

    @abstractmethod
    def find_by_name(self, project_id: int) -> Project:
        """Find a project by ID (method name misleading)."""
        pass

@dataclass
class ProjectServiceImpl(ProjectService):
    """Service layer for managing projects.

    Attributes:
        project_repository (ProjectRepository): Repository to persist and fetch project data.
    """

    project_repository: ProjectRepository

    def create_project(self, create_project_dto: CreateProjectDto) -> Project:
        """Create a project based on the given DTO and persist it."""
        project = ProjectEntity(
            name=create_project_dto.name,
            description=create_project_dto.description,
            start_date=create_project_dto.start_date,
            end_date=create_project_dto.end_date,
            status=create_project_dto.status,
            user_id=create_project_dto.user_id
        )
        logging.info(f"Created project {project.name}")
        self.project_repository.save_or_update(project)
        return project

    def delete_by_id(self, project_id: int) -> None:
        """Delete a project by its ID."""
        self.project_repository.delete_by_id(project_id)

    def find_all_projects(self) -> List[Project]:
        """Return all stored projects."""
        return self.project_repository.find_all()

    def find_by_id(self, project_id: int) -> Project:
        """Find and return a project by its ID."""
        return self.project_repository.find_by_id(project_id)

    def find_by_name(self, project_id: int) -> Project:
        """Find a project by ID (method name misleading)."""
        return self.project_repository.find_by_name(project_id)

    def assign_project_to_user(self, user_id: int, project_id: int) -> None:
        """Assign a project to a user."""
        self.project_repository.assign_project_to_user(user_id, project_id)

    def find_all_sorted_by_date(self, sort_by: str = 'start_date', descending: bool = False):
        """Return all projects sorted by a date field.

        Args:
            sort_by (str): The field to sort by ('start_date' or 'end_date').
            descending (bool): Whether the sorting should be descending.

        Returns:
            List[Project]: Sorted list of projects.
        """
        if sort_by not in {'start_date', 'end_date'}:
            raise ValueError("Invalid sorting field. Use 'start_date' or 'end_date'.")
        return self.project_repository.find_all_sorted_by_date(sort_by, descending=descending)

    def find_all_filtered_by_date(self, input_date: date, filter_by: str = 'start_date'):
        """Return all projects filtered by the specified date field.

        Args:
            input_date (date): The date to filter by.
            filter_by (str): The field to filter ('start_date' or 'end_date').

        Returns:
            List[Project]: Filtered list of projects.
        """
        if filter_by not in {'start_date', 'end_date'}:
            raise ValueError("Invalid filtering field. Use 'start_date' or 'end_date'.")
        return self.project_repository.find_all_filtered_by_date(input_date, filter_by)
