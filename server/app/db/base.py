# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base
from app.models.user import User 
from app.models.service import Service
from app.models.status import Status
