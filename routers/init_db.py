from fastapi import APIRouter
import asyncio
from migrate import create_tables

router = APIRouter(prefix="/init-db", tags=["init-db"])

@router.post("/")
async def init_db():
    await create_tables()
    return {"status": "Database initialized"}
