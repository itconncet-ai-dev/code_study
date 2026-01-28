"""
Models Package - SQLAlchemy ORM models for all database entities.

This package contains all SQLAlchemy ORM models for the AI Code Learning Platform.
All models inherit from the Base class and use the provided mixins for common
functionality like timestamps, soft delete, and UUID primary keys.

Usage:
    from src.models import Base, User, Project, Task

Model Hierarchy:
    Base (DeclarativeBase)
    ├── User
    ├── RefreshToken (belongs to User)
    ├── Project (belongs to User)
    │   └── Task (belongs to Project)
    │       ├── UploadedCode (1:1 with Task)
    │       │   └── CodeFile (belongs to UploadedCode)
    │       ├── LearningDocument (1:1 with Task)
    │       ├── PracticeProblem (belongs to Task, 5 per Task)
    │       ├── Question (belongs to Task and User)
    │       └── Progress (1:1 with Task per User)
"""

from src.models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    model_to_dict,
)
from src.models.code_file import CodeFile
from src.models.learning_document import LearningDocument
from src.models.project import Project
from src.models.refresh_token import RefreshToken
from src.models.task import Task
from src.models.uploaded_code import UploadedCode

# Import models for registration with Base.metadata
from src.models.user import User

# Export base classes and models
__all__ = [
    # Base classes and utilities
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "UUIDPrimaryKeyMixin",
    "model_to_dict",
    # Entity models
    "User",
    "RefreshToken",
    "Project",
    "Task",
    "UploadedCode",
    "CodeFile",
    "LearningDocument",
]

# NOTE: Additional model imports will be added as models are created:
# from src.models.practice_problem import PracticeProblem
# from src.models.question import Question
# from src.models.progress import Progress
