from app.db.configuration import sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Enum
from datetime import datetime, date
from app.config.current_timezone import CURRENT_TIMEZONE
from enum import Enum as PyEnum


class ProjectStatusEnum(PyEnum):
    """Enumeration for project status."""
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"
    ARCHIVED = "Archived"


class TaskStatusEnum(PyEnum):
    """Enumeration for task status."""
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    WAITING_FOR_APPROVAL = "Waiting for Approval"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class UserEntity(sa.Model):
    """Represents a user in the system.

    Attributes:
        id (int): Unique identifier.
        name (str): First name.
        surname (str): Last name.
        email (str): Email address.
    """

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    surname: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(55))

    def to_dict(self) -> dict[str, int | str | None]:
        """Convert user entity to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email
        }

    def __str__(self) -> str:
        return f"USER: {self.id}, {self.name}, {self.surname}, {self.email}"

    def __repr__(self) -> str:
        return f"UserEntity(id={self.id}, name={self.name}, surname={self.surname}, email={self.email})"


class ProjectEntity(sa.Model):
    """Represents a project.

    Attributes:
        id (int): Unique identifier.
        name (str): Project name.
        description (str): Description of the project.
        start_date (date): Start date.
        end_date (date | None): End date.
        status (ProjectStatusEnum): Project status.
        user_id (int): Foreign key to UserEntity.
    """

    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(30))
    description: Mapped[str] = mapped_column(sa.String(255))
    start_date: Mapped[date] = mapped_column(sa.Date)
    end_date: Mapped[date] = mapped_column(sa.Date, nullable=True)
    status: Mapped[ProjectStatusEnum] = mapped_column(sa.Enum(ProjectStatusEnum), default=ProjectStatusEnum.PLANNED)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id'))
    users: Mapped[UserEntity] = relationship("UserEntity", backref="projects")

    def to_dict(self) -> dict[str, int | str | date | None | ProjectStatusEnum]:
        """Convert project entity to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.name,
            'user_id': self.user_id
        }

    def __str__(self) -> str:
        return f"PROJECT: {self.id}, {self.name}, {self.description}, {self.start_date}, {self.end_date} STATUS: {self.status}"

    def __repr__(self):
        return f"ProjectEntity(id={self.id}, name={self.name}, description={self.description}, start_date={self.start_date}, end_date={self.end_date}, status={self.status})"


class TaskEntity(sa.Model):
    """Represents a task assigned to a project.

    Attributes:
        id (int): Unique identifier.
        title (str): Title of the task.
        description (str | None): Description.
        start_date (date | None): Task start.
        end_date (date | None): Task end.
        status (TaskStatusEnum): Current status.
        project_id (int): Associated project.
    """

    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(100))
    description: Mapped[str | None] = mapped_column(sa.String(255))
    start_date: Mapped[date | None] = mapped_column(sa.Date)
    end_date: Mapped[date | None] = mapped_column(sa.Date)
    status: Mapped[TaskStatusEnum] = mapped_column(sa.Enum(TaskStatusEnum), default=TaskStatusEnum.TO_DO)
    project_id: Mapped[int] = mapped_column(sa.ForeignKey('projects.id'))
    project: Mapped[ProjectEntity] = relationship("ProjectEntity", backref="tasks")

    def to_dict(self) -> dict[str, int | str | None | date]:
        """Convert task entity to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'project_id': self.project_id
        }

    def __str__(self) -> str:
        return f"TASK: {self.id}, {self.title}"

    def __repr__(self) -> str:
        return f"TaskEntity(id={self.id}, title={self.title}, status={self.status})"


class CommentEntity(sa.Model):
    """Represents a comment on a task.

    Attributes:
        id (int): Unique identifier.
        content (str): Comment text.
        creation_date (datetime): Timestamp of comment.
        task_id (int): Associated task.
    """

    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    content: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(CURRENT_TIMEZONE))
    task_id: Mapped[int] = mapped_column(sa.ForeignKey('tasks.id'), nullable=False)

    task: Mapped[TaskEntity] = relationship('TaskEntity', backref=sa.backref('comments', lazy=False))

    def to_dict(self) -> dict[str, int | str]:
        """Convert comment entity to dictionary."""
        return {
            'id': self.id,
            'content': self.content,
            'creation_date': self.creation_date.isoformat(),
            'task_id': self.task_id,
        }

    def __str__(self) -> str:
        return f"COMMENT: {self.id}, {self.content}"

    def __repr__(self) -> str:
        return f"CommentEntity(id={self.id}, content={self.content}, task_id={self.task_id})"


class TaskHistoryEntity(sa.Model):
    """Represents a change history record for a task.

    Attributes:
        id (int): Unique identifier.
        change_description (str): Description of the change.
        change_date (datetime): When it happened.
        task_id (int): Related task ID.
    """

    __tablename__ = 'task_history'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    change_description: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    change_date: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(CURRENT_TIMEZONE))
    task_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('tasks.id', ondelete='SET NULL'),
        nullable=True
    )

    task: Mapped[TaskEntity] = relationship('TaskEntity', backref=sa.backref('task_history', lazy=False))

    def to_dict(self) -> dict[str, int | str]:
        """Convert task history entity to dictionary."""
        return {
            'id': self.id,
            'change_description': self.change_description,
            'change_date': self.change_date.isoformat(),
            'task_id': self.task_id
        }

    def __str__(self) -> str:
        return f"TASK HISTORY: {self.id}, {self.change_description}"

    def __repr__(self) -> str:
        return f"TaskHistoryEntity(id={self.id}, change_description={self.change_description}, task_id={self.task_id})"
