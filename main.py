# FastAPI app for Fantasy League Hockey
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import leagues, teams, users, init_db, players, scoring


app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leagues.router)
app.include_router(teams.router)
app.include_router(users.router)
app.include_router(players.router)
app.include_router(scoring.router)
app.include_router(init_db.router)

@app.get("/")
def root():
    return {"message": "Fantasy League Hockey API is running!"}
