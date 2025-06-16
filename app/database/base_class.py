# Import all the models, so that Base has them before being imported by Alembic
from app.models.user import User  # noqa
from app.models.flashcard import Course, Quiz  # noqa

# This will ensure all models are registered with SQLAlchemy
from app.database.base import Base  # noqa 