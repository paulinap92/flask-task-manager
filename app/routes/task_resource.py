from flask_restful import Resource, reqparse
from flask import Response, jsonify, make_response, request
from app.db.repository import (
    ProjectRepository,
    project_repository,
    TaskRepository,
    task_repository
)
from app.db.entity import (
    UserEntity,
    ProjectEntity,
    ProjectStatusEnum,
    TaskStatusEnum,
    TaskEntity
)
from app.service.configuration import task_service
from datetime import datetime, date
import logging
from app.service.dto import CreateTaskDto

from flask_pydantic import validate
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)


class CreateTaskSchema(BaseModel):
    """Schema for task creation."""
    title: str = Field(..., min_length=1, description="Task title")
    description: str = Field(..., min_length=1, description="Task description")
    start_date: date = Field(..., description="Start date in format YYYY-MM-DD")
    end_date: date | None = Field(None, description="End date in format YYYY-MM-DD")
    status: str = Field(..., description="Task status")
    project_id: int = Field(..., ge=1, description="Associated project ID")


class UpdateTaskStatusSchema(BaseModel):
    """Schema for updating task status."""
    status: str = Field(..., description="New task status")


class TaskResourceID(Resource):
    """Resource for retrieving, deleting or updating a task by ID."""

    def get(self, id_: int) -> Response:
        """
        Get a task by its ID.

        Args:
            id_ (int): ID of the task.

        Returns:
            Response: Task data or error message.
        """
        task = task_service.find_by_id(id_)
        if task:
            response = make_response({'app': task.to_dict()}, 200)
            return response
        return {'message': 'Task not found'}, 404

    def delete(self, id_: int) -> Response:
        """
        Delete a task by its ID.

        Args:
            id_ (int): ID of the task to delete.

        Returns:
            Response: Deletion success or failure message.
        """
        task = task_service.find_by_id(id_)
        if task:
            task_service.delete_by_id(id_)
            return {'message': 'Task deleted'}
        return {'message': 'Task not deleted'}, 500

    @validate()
    def put(self, id_: int, body: UpdateTaskStatusSchema) -> Response:
        """
        Update a task's status by ID.

        Args:
            id_ (int): Task ID.
            body (UpdateTaskStatusSchema): New status.

        Returns:
            Response: Update result.
        """
        try:
            task = task_service.find_by_id(id_)
            if not task:
                return {"message": "Task not found"}, 404

            try:
                new_status = TaskStatusEnum[body.status.upper()]
            except KeyError:
                return {"message": f"Invalid status value: {body.status}"}, 400

            task_service.change_status(id_, new_status)
            return {"message": "Task status updated successfully."}, 200

        except Exception as e:
            logging.error(f'Error occurred: {str(e)}')
            return {"message": "Error updating task status", "error": str(e)}, 500


class TaskAddToProjectResource(Resource):
    """Resource for creating a new task and assigning it to a project."""

    @validate()
    def post(self, body: CreateTaskSchema) -> Response:
        """
        Create a task and assign it to a project.

        Args:
            body (CreateTaskSchema): Input task data.

        Returns:
            Response: Success message or error details.
        """
        try:
            title = body.title
            description = body.description
            start_date = body.start_date
            end_date = body.end_date
            status_str = body.status
            project_id = body.project_id

            # Validate status
            try:
                status = TaskStatusEnum[status_str.upper()]
                logging.info(f'Status is valid: {status}')
            except KeyError:
                logging.error(f'Invalid status value: {status_str}')
                return {"message": f"Invalid status value: {status_str}"}, 400

            task = CreateTaskDto(title, description, start_date, end_date, status, project_id)
            task_service.create_task(task)

            # Track task creation in history
            # t1 = task_repository.find_id_by_name(title)
            # task_service.actualize_task_history_after_added(title, t1.id)

            return {"message": "Task added successfully!"}, 201

        except Exception as e:
            logging.error(f'Error occurred: {str(e)}')
            return {"message": "Error processing the request", "error": str(e)}, 400


class TaskSortByStartDate(Resource):
    """Resource to return all tasks sorted by start date."""

    def get(self) -> Response:
        """
        Get all tasks sorted by start date ascending.

        Returns:
            Response: List of sorted tasks.
        """
        tasks = task_service.find_all_sorted_by_date("start_date")
        return {'tasks': [task.to_dict() for task in tasks]}, 200


class TaskFilterByStatus(Resource):
    """Resource to filter tasks by status."""

    def get(self, status: str) -> Response:
        """
        Filter tasks by status.

        Args:
            status (str): Task status to filter.

        Returns:
            Response: List of filtered tasks or error.
        """
        try:
            status_enum = TaskStatusEnum[status.upper()]
        except KeyError:
            return {"message": f"Invalid status value: {status}"}, 400

        tasks = task_service.find_all_filtered_by_status(status_enum)
        return {'tasks': [task.to_dict() for task in tasks]}, 200
