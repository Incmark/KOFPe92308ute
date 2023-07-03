from logging import getLogger

import aio_pika
from fastapi import APIRouter, FastAPI

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.logger import CustomLogger, RabbitMQ

logger = getLogger(__name__)
root_router = APIRouter()
app = FastAPI(title="API SERVICE")

@app.on_event("startup")
async def startup():
    mq = RabbitMQ(settings.RABBITMQ_URI, "logs", aio_pika.ExchangeType.TOPIC)
    await mq.connect()
    app.logger = CustomLogger(mq)

@app.on_event("shutdown")
async def shutdown():
    await app.logger.close()

@root_router.get("/", status_code=200)
async def root() -> dict:
    """
    Root GET
    """
    1/0
    return {'hello': 'world'}


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")