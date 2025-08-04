from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

# Create a SQLAlchemy instance with a custom base class.
# This instance will be configured with the database URI in the main app factory (`create_app`).
sa = SQLAlchemy(model_class=Base)

