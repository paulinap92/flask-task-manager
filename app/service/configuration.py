# from app.service.shops_service import ShopsService
from app.service.user_service import UserServiceImpl
from app.db.repository import user_repository, project_repository, task_repository, comment_repository, task_history_repository
"""
configuration.py

This module initializes and configures service layer implementations by injecting
repository dependencies. It acts as a simple dependency injection container for
the application services.

Services:
    - user_service (UserServiceImpl): Handles user operations.
    - project_service (ProjectServiceImpl): Handles project operations.
    - task_service (TaskServiceImpl): Handles task CRUD and history logging.
    - comment_service (CommentServiceImpl): Handles comment operations.

Dependencies:
    - UserRepository, ProjectRepository, TaskRepository, CommentRepository, TaskHistoryRepository
"""


from app.service.project_service import ProjectServiceImpl
from app.service.task_service import TaskServiceImpl
from app.service.comment_service import CommentServiceImpl



user_service = UserServiceImpl(user_repository)
project_service = ProjectServiceImpl(project_repository)
task_service = TaskServiceImpl(task_repository, project_repository, task_history_repository)
comment_service = CommentServiceImpl(comment_repository, task_repository)