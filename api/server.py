from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db.database import async_session_maker
from db.request import get_tournament_table

app = FastAPI()

# Папки фронта
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
            "score": row.score
        } for row in table
    ])
