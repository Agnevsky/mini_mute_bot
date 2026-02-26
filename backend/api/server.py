from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from ..db.database import async_session_maker
from ..db.request import get_tournament_table

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

app.mount("/static_tournament", StaticFiles(directory=BASE_DIR / "web" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "web" / "templates")

# Страница фронта
@app.get("/tournament")
async def tournament_page(request: Request):
    async with async_session_maker() as session:
        table = await get_tournament_table(session)
    return templates.TemplateResponse("tournament.html", {"request": request, "table": table})

# JSON для JS
@app.get("/tournament/json")
async def tournament_json():
    async with async_session_maker() as session:
        table = await get_tournament_table(session)
    # Конвертируем объекты Tournament в dict
    return JSONResponse(content=[
        {
            "players_name": row.players_name,
            "players_command": row.players_command,
            "games": row.games,
            "games_win": row.games_win,
            "games_lose": row.games_lose,
            "score": row.score,
            "missed_goals": row.missed_goals,
            "score_goals": row.score_goals,
            "different_goals":row.different_goals,
        } for row in table
    ])
