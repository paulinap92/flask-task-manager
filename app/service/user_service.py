"""
user_service.py

This module defines the abstract interface and concrete implementation
of the user service layer. The service encapsulates business logic related to
user creation, retrieval, deletion, and project assignment.

Classes:
    UserService (ABC):
        Abstract base class that defines operations available for user management.

    UserServiceImpl:
        Concrete implementation of UserService using UserRepository.

Dependencies:
    - UserRepository: Access layer to database operations on UserEntity.
    - CreateUserDto: Data transfer object for creating users.
    - User: Domain model representing a user.
    - Project: Domain model representing a project.
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod

from app.service.model import User, Project
from app.db.repository import UserRepository
from app.service.dto import CreateUserDto
from app.db.entity import UserEntity

import logging
logging.basicConfig(level=logging.INFO)


class UserService(ABC):
    """Abstract interface for user-related operations."""

    @abstractmethod
    def create_user(self, create_user_dto: CreateUserDto) -> User:
        """Create a new user and return the result as a domain model."""
        pass

    @abstractmethod
    def delete_by_id(self, user_id: int) -> None:
        """Delete a user by ID."""
        pass

    @abstractmethod
    def find_all_users(self) -> list[User]:
        """Return a list of all users."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User:
        """Find a user by their ID."""
        pass

    def get_projects(self, user_id: int) -> list[Project]:
        """Get all projects associated with a user."""
        pass

    def assign_user_to_project(self, user_id: int, project_id: int) -> None:
        """Assign a user to a specific project."""
        pass


@dataclass
class UserServiceImpl(UserService):
    """Service layer implementation for managing users.

    Attributes:
        user_repository (UserRepository): The repository used to access user data.
    """

    user_repository: UserRepository

    def create_user(self, create_user_dto: CreateUserDto) -> User:
        """Create and persist a new user entity based on DTO."""
        existing = self.user_repository.find_by_email(create_user_dto.email)
        if existing:
            raise ValueError("User with this email already exists.")

        user = UserEntity(
            name=create_user_dto.name,
            surname=create_user_dto.surname,
            email=create_user_dto.email
        )
        self.user_repository.save_or_update(user)
        return user

    def delete_by_id(self, user_id: int) -> None:
        """Delete a user entity by its ID."""
        self.user_repository.delete_by_id(user_id)

    def find_all_users(self) -> list[User]:
        """Retrieve and return all users."""
        return self.user_repository.find_all()

    def find_by_id(self, user_id: int) -> User:
        """Find and return a user by ID."""
        return self.user_repository.find_by_id(user_id)

    def get_user_projects(self, user_id: int) -> list[Project]:
        """Return a list of projects assigned to the user."""
        return self.user_repository.get_user_projects(user_id)

    def find_user_by_name(self, name: str) -> User:
        """Search for a user by their name."""
        return self.user_repository.find_by_name(name)

    def assign_user_to_project(self, user_id: int, project_id: int) -> None:
        """Assign a user to a given project."""
        self.user_repository.assign_user_to_project(user_id, project_id)
