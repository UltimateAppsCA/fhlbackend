
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from ..db import get_db
from ..models import Player, League, FantasyTeam, RosterSpot, User
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os

router = APIRouter(prefix="/players", tags=["players"])

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

class PlayerCreate(BaseModel):
    name: str
    position: str
    nhl_team: str
    stats: dict = {}

@router.post("/", status_code=201)
async def add_player(player: PlayerCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    db_player = Player(name=player.name, position=player.position, nhl_team=player.nhl_team, stats=player.stats)
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)
    return {"id": db_player.id, "name": db_player.name, "position": db_player.position, "nhl_team": db_player.nhl_team}

@router.get("/")
async def list_players(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Player))
    players = result.scalars().all()
    return [{"id": p.id, "name": p.name, "position": p.position, "nhl_team": p.nhl_team, "stats": p.stats} for p in players]

# Simple draft pick endpoint (assigns player to team if available)
class DraftPickRequest(BaseModel):
    team_id: int
    player_id: int

@router.post("/draft_pick")
async def draft_pick(req: DraftPickRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # Check if player is already on a team
    result = await db.execute(select(RosterSpot).where(RosterSpot.player_id == req.player_id))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Player already drafted")
    roster_spot = RosterSpot(team_id=req.team_id, player_id=req.player_id)
    db.add(roster_spot)
    await db.commit()
    return {"team_id": req.team_id, "player_id": req.player_id, "drafted": True}
