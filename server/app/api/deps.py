from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.future import select

from app.core.auth import oauth2_scheme
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

class TokenData(BaseModel):
    id: Optional[int] = None

async def get_db() -> AsyncGenerator:
    session = None
    try:
        async with SessionLocal() as session:
            yield session
    except Exception as e:
        if session is not None:
            await session.rollback()
            await session.close()
        raise e
    else:
        if session is not None:
            await session.close()


async def get_current_user(
    db = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    user = (await db.execute(select(User).where(
        User.id == token_data.id))).scalars().first()
    if user is None:
        raise credentials_exception
    return user