
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from ..db import get_db
from ..models import FantasyTeam, User, League, Player, RosterSpot
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os

router = APIRouter(prefix="/teams", tags=["teams"])

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

class TeamCreate(BaseModel):
    name: str
    owner_id: int
    league_id: int

class AddPlayerRequest(BaseModel):
    player_id: int

@router.post("/", status_code=201)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    db_team = FantasyTeam(name=team.name, owner_id=user.id, league_id=team.league_id)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return {"id": db_team.id, "name": db_team.name, "owner_id": db_team.owner_id, "league_id": db_team.league_id}

@router.get("/")
async def list_teams(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(FantasyTeam))
    teams = result.scalars().all()
    return [{"id": t.id, "name": t.name, "owner_id": t.owner_id, "league_id": t.league_id} for t in teams]

@router.post("/{team_id}/add_player")
async def add_player_to_team(team_id: int, req: AddPlayerRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    team = await db.get(FantasyTeam, team_id)
    player = await db.get(Player, req.player_id)
    if not team or not player:
        raise HTTPException(status_code=404, detail="Team or player not found")
    if team.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your team")
    roster_spot = RosterSpot(team_id=team_id, player_id=req.player_id)
    db.add(roster_spot)
    await db.commit()
    return {"team_id": team_id, "player_id": req.player_id}

@router.post("/{team_id}/remove_player")
async def remove_player_from_team(team_id: int, req: AddPlayerRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    team = await db.get(FantasyTeam, team_id)
    if not team or team.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your team")
    result = await db.execute(select(RosterSpot).where(RosterSpot.team_id == team_id, RosterSpot.player_id == req.player_id))
    spot = result.scalar()
    if not spot:
        raise HTTPException(status_code=404, detail="Player not on team")
    await db.delete(spot)
    await db.commit()
    return {"team_id": team_id, "player_id": req.player_id, "removed": True}
