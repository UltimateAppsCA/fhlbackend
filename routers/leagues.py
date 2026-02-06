from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from db import get_db
from models import League, User
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os

router = APIRouter(prefix="/leagues", tags=["leagues"])

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

class LeagueCreate(BaseModel):
    name: str
    settings: dict = {}

@router.post("/", status_code=201)
async def create_league(league: LeagueCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    db_league = League(name=league.name, settings=league.settings, commissioner_id=user.id)
    db.add(db_league)
    await db.commit()
    await db.refresh(db_league)
    return {"id": db_league.id, "name": db_league.name, "settings": db_league.settings}

@router.get("/")
async def list_leagues(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(League))
    leagues = result.scalars().all()
    return [{"id": l.id, "name": l.name, "settings": l.settings} for l in leagues]
