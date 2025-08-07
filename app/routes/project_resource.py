from flask_restful import Resource
from flask import Response, jsonify, make_response
from flask_pydantic import validate
from pydantic import BaseModel, Field
from datetime import datetime, date
import logging

from app.service.model import Project
from app.db.repository import (
    ProjectRepository,
    project_repository
)
from app.db.entity import (
    UserEntity,
    ProjectEntity,
    ProjectStatusEnum
)
from app.service.configuration import project_service
from app.service.dto import CreateProjectDto

logging.basicConfig(level=logging.INFO)

# 📦 Request schema for project creation
class CreateProjectSchema(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the project")
    description: str = Field(..., min_length=1, description="Project description")
    start_date: date = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: date = Field(None, description="End date in YYYY-MM-DD format")
    status: str = Field(..., description="Status of the project")
    user_id: int = Field(..., ge=1, description="User ID that owns the project")


class ProjectResourceID(Resource):
    """Handles GET and DELETE for a specific project by ID."""

    def get(self, id_: int) -> Response:
        """Get project by ID."""
        project = project_service.find_by_id(id_)
        if project:
            response = make_response({'app': project.to_dict()}, 200)
            return response
        return {'message': 'Project not found'}, 404

    def delete(self, id_: int) -> Response:
        """Delete project by ID."""
        project = project_service.find_by_id(id_)
        if project:
            project_service.delete_by_id(id_)
            return {'message': 'Project deleted'}
        return {'message': 'Project not deleted'}, 500


class ProjectResource(Resource):
    """Handles GET for a specific project by name."""

    def get(self, name: str) -> Response:
        """Get project by name."""
        project = project_service.find_by_name(name)
        if project:
            return {'project': project.to_dict()}
        return {'message': 'Project not found'}, 404


class ProjectResourceSortByStartDateAsc(Resource):
    """Handles GET for all projects sorted by start date ascending."""

    def get(self) -> Response:
        return {'projects': [project.to_dict() for project in project_service.find_all_sorted_by_date('start_date', False)]}


class ProjectResourceFilterByStartDate(Resource):
    """Handles GET for filtering projects by a given start date."""

    def get(self, input_date: str) -> Response:
        try:
            parsed_date = datetime.strptime(input_date, '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400
        return {'projects': [project.to_dict() for project in project_service.find_all_filtered_by_date(parsed_date, 'start_date')]}


class ProjectResourceAdd(Resource):
    """Handles POST for adding a new project."""

    @validate()
    def post(self, body: CreateProjectSchema) -> Response:
        try:
            try:
                status = ProjectStatusEnum[body.status]  # Convert status string to enum
            except ValueError as e:
                logging.error(f'Invalid status value: {body.status}')
                return {"message": str(e)}, 400

            project = CreateProjectDto(
                name=body.name,
                description=body.description,
                start_date=body.start_date,
                end_date=body.end_date,
                status=status,
                user_id=body.user_id
            )
            project_service.create_project(project)
            return {"message": "Project added successfully!"}, 201

        except Exception as e:
            logging.error(f'Error occurred: {str(e)}')
            return {"message": "Error processing the request", "error": str(e)}, 400


class ProjectListResource(Resource):
    """Handles GET for listing all projects."""

    def get(self) -> Response:
        return {'projects': [project.to_dict() for project in project_service.find_all_projects()]}
