"""
comment_service.py

This module defines the abstract interface and concrete implementation of services
related to handling comments in the task management system.

Classes:
    CommentService (ABC):
        Abstract base class specifying operations related to comments.

    CommentServiceImpl:
        Concrete implementation for creating, deleting, and retrieving comments.

Methods:
    create_task(create_comment_dto: CreateCommentDto) -> Comment:
        Creates a new comment associated with a task.

    delete_by_id(comment_id: int) -> None:
        Deletes a comment by its ID.

    find_all_comments() -> list[Comment]:
        Returns all stored comments.

    find_by_id(comment_id: int) -> Comment:
        Finds a comment by its ID.

    find_by_name(comment_id: int) -> Comment:
        (Method exists but is redundant or misnamed; comments are typically not searched by name.)

Dependencies:
    - CommentRepository, TaskRepository
    - CreateCommentDto, CommentEntity
    - Task validation to ensure comment is assigned to an existing task
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod


from app.service.model import Comment
from app.db.repository import CommentRepository, comment_repository, TaskRepository, task_repository
from app.service.dto import CreateCommentDto
from app.db.entity import CommentEntity

import logging
logging.basicConfig(level=logging.INFO)

class CommentService(ABC):
    """Abstract interface for comment-related operations."""

    @abstractmethod
    def create_task(self, create_comment_dto: CreateCommentDto) -> Comment:
        """Create a comment associated with a task."""
        pass

    @abstractmethod
    def delete_by_id(self, comment_id: int) -> None:
        """Delete a comment by its ID."""
        pass

    @abstractmethod
    def find_all_comments(self) -> list[Comment]:
        """Return all comments."""
        pass

    @abstractmethod
    def find_by_id(self, task_id: int) -> Comment:
        """Find a comment by ID."""
        pass

@dataclass
class CommentServiceImpl(CommentService):
    """Service class responsible for comment operations.

    Attributes:
        comment_repository (CommentRepository): Repository for comment persistence.
        task_repository (TaskRepository): Repository to validate task existence.
    """

    comment_repository: CommentRepository
    task_repository: TaskRepository

    def create_task(self, create_comment_dto: CreateCommentDto) -> Comment:
        """Create and store a comment, validating task existence first."""
        if self.task_repository.find_by_id(create_comment_dto.task_id):
            comment = CommentEntity(
                content=create_comment_dto.content,
                creation_date=create_comment_dto.creation_date,
                task_id=create_comment_dto.task_id
            )
            self.comment_repository.save_or_update(comment)
            return comment
        else:
            raise ValueError(f"Task with ID {create_comment_dto.task_id} does not exist.")

    def delete_by_id(self, comment_id: int) -> None:
        """Delete a comment by its ID."""
        self.comment_repository.delete_by_id(comment_id)

    def find_all_comments(self) -> list[Comment]:
        """Retrieve all stored comments."""
        return self.comment_repository.find_all()

    def find_by_id(self, comment_id: int) -> Comment:
        """Find a comment by its ID."""
        return self.comment_repository.find_by_id(comment_id)

    def find_by_name(self, comment_id: int) -> Comment:
        """(Possibly misnamed) find_by_name method, using comment_id."""
        return self.comment_repository.find_by_name(comment_id)
