"""
repository.py

This module defines a set of generic and entity-specific repository classes
for performing CRUD operations on SQLAlchemy models. It follows the repository
pattern to encapsulate persistence logic and separate it from application logic.

Classes:
    CrudRepository[T] (ABC):
        An abstract base class that defines a generic interface for
        basic CRUD operations on entities of type T.

    CrudRepositoryORM[T]:
        A generic implementation of CrudRepository using SQLAlchemy ORM.
        Supports automatic entity type inference.

    UserRepository:
        Repository for performing operations related to UserEntity.

    ProjectRepository:
        Repository for ProjectEntity, includes date filtering/sorting.

    TaskRepository:
        Repository for TaskEntity, includes methods for changing task status
        and searching by project ID or title.

    TaskHistoryRepository:
        Repository for TaskHistoryEntity, allows lookup by task ID.

    CommentRepository:
        Repository for CommentEntity, allows lookup by task ID.

Global Instances:
    user_repository: Instance of UserRepository.
    comment_repository: Instance of CommentRepository.
    project_repository: Instance of ProjectRepository.
    task_repository: Instance of TaskRepository.
    task_history_repository: Instance of TaskHistoryRepository.
"""

from abc import ABC, abstractmethod
from flask_sqlalchemy import SQLAlchemy
from app.db.configuration import sa
from app.db.entity import (
    UserEntity,
    ProjectEntity,
    ProjectStatusEnum,
    TaskStatusEnum,
    TaskEntity,
    CommentEntity,
    TaskHistoryEntity
)
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)

# -----------------------------------------------------------------------
# [ Generic CRUD Interface ]
# -----------------------------------------------------------------------

class CrudRepository[T](ABC):
    """Generic interface for CRUD operations.

    Methods:
        save_or_update(entity): Saves or updates a single entity.
        save_or_update_many(entities): Saves or updates a list of entities.
        find_by_id(entity_id): Returns a single entity by ID.
        find_all(): Returns all entities.
        delete_by_id(entity_id): Deletes an entity by ID.
        delete_all(): Deletes all entities.
    """
    """Generic interface for CRUD operations."""

    @abstractmethod
    def save_or_update(self, entity: T) -> None:
        pass

    @abstractmethod
    def save_or_update_many(self, entities: list[T]) -> None:
        pass

    @abstractmethod
    def find_by_id(self, entity_id: int) -> T | None:
        pass

    @abstractmethod
    def find_all(self) -> list[T]:
        pass

    @abstractmethod
    def delete_by_id(self, entity_id: int) -> None:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass


# -----------------------------------------------------------------------
# [ SQLAlchemy ORM CRUD Implementation ]
# -----------------------------------------------------------------------

class CrudRepositoryORM[T: sa.Model](CrudRepository[T]):
    """Generic SQLAlchemy implementation of CrudRepository.

    Args:
        db (SQLAlchemy): SQLAlchemy database instance.

    Methods:
        save_or_update(entity): Adds entity to session and commits.
        save_or_update_many(entities): Bulk add and commit.
        find_by_id(entity_id): Query by primary key.
        find_all(): Query all records.
        delete_by_id(entity_id): Delete record by primary key.
        delete_all(): Delete all records of the model.
    """
    """Generic SQLAlchemy implementation of CrudRepository."""

    def __init__(self, db: SQLAlchemy) -> None:
        self.sa = db
        self.entity_type = self.__class__.__orig_bases__[0].__args__[0]

    def save_or_update(self, entity: T) -> None:
        logging.info(f"Saving entity: {entity}")
        self.sa.session.add(entity)
        self.sa.session.commit()

    def save_or_update_many(self, entities: list[T]) -> None:
        self.sa.session.add_all(entities)
        self.sa.session.commit()

    def find_by_id(self, entity_id: int) -> T | None:
        return self.sa.session.query(self.entity_type).get(entity_id)

    def find_all(self) -> list[T]:
        logging.info(f"Fetching all from {self.entity_type}")
        return self.sa.session.query(self.entity_type).all()

    def delete_by_id(self, entity_id: int) -> None:
        entity = self.find_by_id(entity_id)
        if entity:
            self.sa.session.delete(entity)
            self.sa.session.commit()

    def delete_all(self) -> None:
        self.sa.session.query(self.entity_type).delete()
        self.sa.session.commit()


# -----------------------------------------------------------------------
# [ Repositories for Specific Entities ]
# -----------------------------------------------------------------------

class UserRepository(CrudRepositoryORM[UserEntity]):
    """Repository for UserEntity with additional methods for
    searching by name and assigning users to projects."""

    def find_by_name(self, name: str) -> UserEntity | None:
        """Find a user by their name."""
        return self.sa.session.query(UserEntity).filter_by(name=name).first()

    def get_user_projects(self, user_id: int):
        """Return all projects assigned to a specific user."""
        user = self.sa.session.query(UserEntity).filter_by(id=user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")
        return user.projects

    def assign_user_to_project(self, user_id: int, project_id: int) -> None:
        """Assign a user to a project if not already assigned."""
        user = self.sa.session.query(UserEntity).filter_by(id=user_id).first()
        project = self.sa.session.query(ProjectEntity).filter_by(id=project_id).first()

        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")
        if not project:
            raise ValueError(f"Project with ID {project_id} does not exist.")

        if user not in project.users:
            project.users.append(user)
            self.sa.session.commit()
        else:
            raise ValueError(f"User with ID {user_id} is already assigned to project with ID {project_id}.")

    def find_by_email(self, email: str) -> UserEntity | None:
        return sa.session.query(UserEntity).filter_by(email=email).first()


class ProjectRepository(CrudRepositoryORM[ProjectEntity]):
    """Repository for ProjectEntity with additional methods
    for filtering and sorting by dates."""

    def find_by_name(self, name: str) -> ProjectEntity | None:
        """Find a project by its name."""
        return self.sa.session.query(ProjectEntity).filter_by(name=name).first()

    def find_all_sorted_by_date(self, sort_by: str = 'start_date', descending: bool = False) -> list[ProjectEntity]:
        """Return all projects sorted by a date field."""
        if sort_by not in {'start_date', 'end_date'}:
            raise ValueError("Invalid sort field. Use 'start_date' or 'end_date'.")
        order = desc(getattr(ProjectEntity, sort_by)) if descending else asc(getattr(ProjectEntity, sort_by))
        return self.sa.session.query(ProjectEntity).order_by(order).all()

    def find_all_filtered_by_date(self, input_date: date, filter_by: str = 'start_date') -> list[ProjectEntity]:
        """Filter projects by exact date match on a given date field."""
        if filter_by not in {'start_date', 'end_date'}:
            raise ValueError("Invalid filter field. Use 'start_date' or 'end_date'.")
        return self.sa.session.query(ProjectEntity).filter(getattr(ProjectEntity, filter_by) == input_date).all()


class TaskRepository(CrudRepositoryORM[TaskEntity]):
    """Repository for TaskEntity with support for searching
    by project and changing task status."""

    def find_id_by_name(self, title: str) -> TaskEntity | None:
        """Find a task by its title."""
        return self.sa.session.query(TaskEntity).filter_by(title=title).first()

    def find_by_project_id(self, project_id: int) -> list[TaskEntity]:
        """Get all tasks that belong to a specific project."""
        return self.sa.session.query(TaskEntity).filter_by(project_id=project_id).all()

    def change_status(self, task_id: int, new_status: TaskStatusEnum) -> TaskEntity | None:
        """Update the status of a task."""
        task = self.sa.session.query(TaskEntity).filter_by(id=task_id).first()
        if task:
            task.status = new_status
            self.sa.session.commit()
            return task
        return None

    def find_all_sorted_by_date(self, sort_by: str = 'start_date', descending: bool = False) -> list[TaskEntity]:
        """Return all tasks sorted by a date field."""
        if sort_by not in {'start_date', 'end_date'}:
            raise ValueError("Invalid sort field. Use 'start_date' or 'end_date'.")
        order = desc(getattr(TaskEntity, sort_by)) if descending else asc(getattr(TaskEntity, sort_by))
        return self.sa.session.query(TaskEntity).order_by(order).all()

    def find_by_status(self, status: TaskStatusEnum) -> list[TaskEntity]:
        """Get all tasks that belong to a specific project."""
        return self.sa.session.query(TaskEntity).filter_by(status=status).all()


class TaskHistoryRepository(CrudRepositoryORM[TaskHistoryEntity]):
    """Repository for TaskHistoryEntity allowing lookup by task ID."""

    def find_by_task_id(self, task_id: int) -> list[TaskHistoryEntity]:
        """Get task history entries for a given task."""
        return self.sa.session.query(TaskHistoryEntity).filter_by(task_id=task_id).all()


class CommentRepository(CrudRepositoryORM[CommentEntity]):
    """Repository for CommentEntity allowing lookup by task ID."""

    def find_by_task_id(self, task_id: int) -> list[CommentEntity]:
        """Get all comments related to a specific task."""
        return self.sa.session.query(CommentEntity).filter_by(task_id=task_id).all()


# -----------------------------------------------------------------------
# [ Repository Instances ]
# -----------------------------------------------------------------------

user_repository = UserRepository(sa)
comment_repository = CommentRepository(sa)
project_repository = ProjectRepository(sa)
task_repository = TaskRepository(sa)
task_history_repository = TaskHistoryRepository(sa)
