
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models import FantasyTeam, Player, RosterSpot, User
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os

router = APIRouter(prefix="/scoring", tags=["scoring"])

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

def default_scoring_rules():
    return {
        'goals': 3.0,
        'assists': 2.0,
        'shots': 0.5,
        'blocks': 0.5,
        'hits': 0.5,
        'wins': 5.0,
        'shutouts': 3.0
    }

def calculate_player_score(player, scoring_rules):
    score = 0.0
    for stat, value in (player.stats or {}).items():
        multiplier = scoring_rules.get(stat, 0)
        score += value * multiplier
    return score

def calculate_team_score(team, players, scoring_rules):
    return sum(calculate_player_score(p, scoring_rules) for p in players)

@router.get("/team/{team_id}")
async def get_team_score(team_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    scoring_rules = default_scoring_rules()
    team = await db.get(FantasyTeam, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    result = await db.execute(select(RosterSpot).where(RosterSpot.team_id == team_id))
    spots = result.scalars().all()
    player_ids = [spot.player_id for spot in spots]
    if not player_ids:
        return {"team_id": team_id, "score": 0}
    result = await db.execute(select(Player).where(Player.id.in_(player_ids)))
    players = result.scalars().all()
    score = calculate_team_score(team, players, scoring_rules)
    return {"team_id": team_id, "score": score}

@router.get("/matchup")
async def play_matchup(team1_id: int, team2_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    scoring_rules = default_scoring_rules()
    team1 = await db.get(FantasyTeam, team1_id)
    team2 = await db.get(FantasyTeam, team2_id)
    if not team1 or not team2:
        raise HTTPException(status_code=404, detail="One or both teams not found")
    # Get players for each team
    result1 = await db.execute(select(RosterSpot).where(RosterSpot.team_id == team1_id))
    player_ids1 = [spot.player_id for spot in result1.scalars().all()]
    result2 = await db.execute(select(RosterSpot).where(RosterSpot.team_id == team2_id))
    player_ids2 = [spot.player_id for spot in result2.scalars().all()]
    result = await db.execute(select(Player).where(Player.id.in_(player_ids1 + player_ids2)))
    all_players = {p.id: p for p in result.scalars().all()}
    score1 = calculate_team_score(team1, [all_players[pid] for pid in player_ids1 if pid in all_players], scoring_rules)
    score2 = calculate_team_score(team2, [all_players[pid] for pid in player_ids2 if pid in all_players], scoring_rules)
    return {"team1_id": team1_id, "score1": score1, "team2_id": team2_id, "score2": score2}
