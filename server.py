import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from db.database import async_session_maker
from db.models import Tournament
from sqlalchemy import select

app = FastAPI()

# Подключаем статические файлы фронта
app.mount("/", StaticFiles(directory="webapp", html=True), name="web")

@app.get("/api/tournament")
async def get_tournament():
    async with async_session_maker() as session:
        result = await session.execute(select(Tournament))
        tournaments = result.scalars().all()
    return [
        {
            "players_command": t.players_command,
            "players_name": t.players_name,
            "games": t.games,
            "games_win": t.games_win,
            "games_lose": t.games_lose,
            "score": t.score,
            "missed_goals": t.missed_goals,
            "score_goals": t.score_goals,
            "different_goals": t.different_goals
        } for t in tournaments
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
