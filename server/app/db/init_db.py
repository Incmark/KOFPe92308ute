import logging

from sqlalchemy.future import select

# from app import crud, schemas
from app.models.service import Service
from app.models.status import Status
from app.core.config import settings
from app.db import defaults

logger = logging.getLogger(__name__)


async def init_db(db) -> None:
    # Base.metadata.create_all(bind=engine)
        srv = (await db.execute(select(Service))).scalars().all()
        sts = (await db.execute(select(Status))).scalars().all()
        def_srv = [Service(**s) for s in defaults.services]
        def_sts = [Status(**s) for s in defaults.statuses]
        db.add_all(
            filter(lambda x: not x in srv, def_srv))
        db.add_all(
            filter(lambda x: not x in sts, def_sts))
        await db.commit()