from flask_restful import Resource
from flask import Response, jsonify, make_response
from flask_pydantic import validate
from pydantic import BaseModel, Field
from datetime import datetime, date
from zoneinfo import ZoneInfo
import logging

from app.db.repository import (
    CommentRepository,
    comment_repository
)
from app.db.entity import (
    TaskStatusEnum,
    TaskEntity,
    CommentEntity
)
from app.service.configuration import comment_service
from app.service.dto import CreateCommentDto

logging.basicConfig(level=logging.INFO)

# 🌍 Timezone setup (used for timestamping comments)
from app.config.current_timezone import CURRENT_TIMEZONE

# 🧾 Request schema for adding a comment
class CreateCommentSchema(BaseModel):
    content: str = Field(..., min_length=1, description="Content of the comment")
    task_id: int = Field(..., ge=1, description="ID of the task to which the comment belongs")


class CommentResourceID(Resource):
    """
    Handles retrieving, updating, and deleting a comment by its unique ID.
    """

    def get(self, id_: int) -> Response:
        """
        Retrieve a comment by ID.
        Returns 200 and comment data if found, 404 if not found.
        """
        comment = comment_service.find_by_id(id_)
        if comment:
            response = make_response({'app': comment.to_dict()}, 200)
            return response
        return {'message': 'Comment not found'}, 404

    def delete(self, id_: int) -> Response:
        """
        Delete a comment by ID.
        Returns 200 if successfully deleted, 500 otherwise.
        """
        comment = comment_service.find_by_id(id_)
        if comment:
            comment_service.delete_by_id(id_)
            return {'message': 'Comment deleted'}, 200
        return {'message': 'Comment not deleted'}, 500

    @validate()
    def put(self, id_: int, body: CreateCommentSchema) -> Response:
        """
        Update an existing comment's content and task_id.
        Timestamps the update using the Warsaw timezone.
        Returns 200 if successful, 404 or 500 otherwise.
        """
        try:
            comment = comment_service.find_by_id(id_)
            if not comment:
                return {'message': 'Comment not found'}, 404

            creation_date = datetime.now(CURRENT_TIMEZONE)

            updated_comment = CreateCommentDto(
                content=body.content,
                creation_date=creation_date,
                task_id=body.task_id
            )

            comment_service.update_by_id(id_, updated_comment)
            return {'message': 'Comment updated successfully!'}, 200

        except Exception as e:
            logging.error(f'Error occurred while updating: {str(e)}')
            return {'message': 'Error updating the comment', 'error': str(e)}, 500


class CommentAddToTaskResource(Resource):
    """
    Handles creation of a new comment associated with a task.
    """

    @validate()
    def post(self, body: CreateCommentSchema) -> Response:
        """
        Create a new comment for a specific task.
        Accepts JSON body with 'content' and 'task_id'.
        Automatically timestamps the comment with Warsaw timezone.
        Returns 201 if successful, 400 otherwise.
        """
        try:
            creation_date = datetime.now(CURRENT_TIMEZONE)

            # Create and store the comment
            comment = CreateCommentDto(
                content=body.content,
                creation_date=creation_date,
                task_id=body.task_id
            )
            comment_service.create_task(comment)
            return {"message": "Comment added successfully!"}, 201

        except Exception as e:
            logging.error(f'Error occurred: {str(e)}')
            return {"message": "Error processing the request", "error": str(e)}, 400
