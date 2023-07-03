from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from random import randint
from app import schemas
from app.api import deps
from app.models.user import User
from app.models.status import Status

router = APIRouter()


@router.get("/int", response_model=schemas.RandomInt)
async def random_int(db=Depends(deps.get_db),
                     current_user: User = Depends(deps.get_current_user)):
    """
    Generate random int.
    """
    if current_user.status_id == None:
        raise HTTPException(
            status_code=410,
            detail="You have no active subscription now",
        )
    status = await db.get(Status, current_user.status_id)
    if not status.lifetime and (
        datetime.utcnow() - current_user.status_purchased_time
    ).total_seconds() > status.plan.total_seconds():
        raise HTTPException(
            status_code=410,
            detail="Your subscription is ended",
        )
    value = randint(0, 100)
    return schemas.RandomInt(value=value)
