from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from ..db.database import async_session_maker
from ..db.request import get_tournament_table, get_game_results

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

@app.get("/results/json")
async def results_json():
    async with async_session_maker() as session:
        results = await get_game_results(session)
    return JSONResponse(content=[
        {
            "game": r.id,
            "player1": r.player1,
            "score1": r.score1,
            "score2": r.score2,
            "player2": r.player2,
            "is_extra_time": r.is_extra_time,
            "is_shootout": r.is_shootout,
            "team1": r.team1,
            "team2": r.team2,
        } for r in results
    ])


@app.get("/head2head/json")
async def head2head_json():
    async with async_session_maker() as session:
        results = await get_game_results(session)
    
    # Считаем очки в личных встречах
    h2h = {}
    
    for r in results:
        p1, p2 = r.player1, r.player2
        key = tuple(sorted([p1, p2]))
        
        if key not in h2h:
            h2h[key] = {p1: 0, p2: 0}
        
        if r.is_extra_time:
            if r.score1 > r.score2:
                h2h[key][p1] = h2h[key].get(p1, 0) + 2
                h2h[key][p2] = h2h[key].get(p2, 0) + 1
            else:
                h2h[key][p2] = h2h[key].get(p2, 0) + 2
                h2h[key][p1] = h2h[key].get(p1, 0) + 1
        else:
            if r.score1 > r.score2:
                h2h[key][p1] = h2h[key].get(p1, 0) + 3
            elif r.score2 > r.score1:
                h2h[key][p2] = h2h[key].get(p2, 0) + 3
    
    return JSONResponse(content={
        f"{k[0]}_{k[1]}": v for k, v in h2h.items()
    })