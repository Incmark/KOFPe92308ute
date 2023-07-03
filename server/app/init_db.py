import logging
import asyncio
from app.db.init_db import init_db
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    async with SessionLocal() as db:
        await init_db(db)


if __name__ == "__main__":
    asyncio.run(main())
