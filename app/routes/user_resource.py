from flask_restful import Resource
from flask import Response, jsonify, make_response, request
from app.db.repository import (
    UserRepository,
    user_repository
)
from app.db.entity import (
    UserEntity,
    ProjectEntity,
    ProjectStatusEnum
)
from app.service.configuration import user_service
from datetime import datetime, date
import logging

from app.service.dto import CreateUserDto

from flask_pydantic import validate
from pydantic import BaseModel, EmailStr, Field

logging.basicConfig(level=logging.INFO)


class CreateUserSchema(BaseModel):
    """
    Input schema for creating a user.

    Attributes:
        name (str): Optional first name of the user.
        surname (str): Required last name of the user.
        email (EmailStr): User email address (validated).
    """
    name: str = Field(default=None, min_length=1)
    surname: str = Field(..., min_length=1, description="Surname is required")
    email: EmailStr


class UserResource(Resource):
    """
    Resource for fetching a user by name.
    """

    def get(self, name: str) -> Response:
        """
        Retrieve a user by their name.

        Args:
            name (str): The name of the user.

        Returns:
            Response: JSON with user data or 404 if not found.
        """
        user = user_service.find_user_by_name(name)
        if user:
            return make_response({'app': user.to_dict()}, 200)
        return {'message': 'User not found'}, 404


class UserAddResource(Resource):
    """
    Resource for adding a new user.
    """

    @validate()
    def post(self, body: CreateUserSchema):
        """
        Create a new user from validated request data.

        Args:
            body (CreateUserSchema): Validated input data.

        Returns:
            Response: JSON with created user data or 500 on failure.
        """
        try:
            user_dto = CreateUserDto(
                name=body.name,
                surname=body.surname,
                email=body.email
            )
            created_user = user_service.create_user(user_dto)
            return jsonify({'app': created_user.to_dict(), 'status': 201})
        except ValueError as ve:
            # user with the same email exists
            return {'message': str(ve)}, 409
        except Exception as e:
            logging.error(e.args[0])
            return {'message': 'Cannot create user'}, 500


class UserProjectResource(Resource):
    """
    Resource for retrieving all projects assigned to a user.
    """

    def get(self, id_: int) -> Response:
        """
        Get all projects assigned to a user by user ID.

        Args:
            id_ (int): The ID of the user.

        Returns:
            Response: JSON with projects or 404 if none found.
        """
        try:
            projects = user_service.get_user_projects(id_)
            if not projects:
                return {'message': 'No projects found for the user'}, 404
            return make_response(jsonify({'projects': [p.to_dict() for p in projects]}), 200)
        except ValueError as e:
            return {'message': str(e)}, 404
        except Exception as e:
            return {'message': f"An error occurred: {str(e)}"}, 500


class UserResourceID(Resource):
    """
    Resource for deleting a user by ID.
    """

    def delete(self, id_: int) -> Response:
        """
        Delete a user by their ID.

        Args:
            id_ (int): The ID of the user.

        Returns:
            Response: JSON message indicating result.
        """
        user = user_service.find_by_id(id_)
        if user:
            user_service.delete_by_id(id_)
            return {'message': 'User deleted'}, 200
        return {'message': 'User not deleted'}, 500

    def get(self, id_: int) -> Response:
        """
        Retrieve a user by their name.

        Args:
            name (str): The name of the user.

        Returns:
            Response: JSON with user data or 404 if not found.
        """
        user = user_service.find_by_id(id_)
        if user:
            return make_response({'app': user.to_dict()}, 200)
        return {'message': 'User not found'}, 404

class UserListResource(Resource):
    """
    Resource for retrieving all users.
    """

    def get(self) -> Response:
        """
        Get a list of all users.

        Returns:
            Response: JSON array of users.
        """
        users = user_service.find_all_users()
        return {'user': [user.to_dict() for user in users]}
