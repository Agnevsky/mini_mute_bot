import openpyxl
from io import BytesIO

def create_tournament_excel(players):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Турнирная таблица"

    headers = ["Место", "Игрок", "Команда", "Игры", "Победы", "Поражения", "Очки", "ЗГ", "ПГ", "Разница"]
    ws.append(headers)

    for i, p in enumerate(players, start=1):
        ws.append([
            i,
            p.players_name,
            p.players_command,
            p.games,
            p.games_win,
            p.games_lose,
            p.score,
            p.score_goals,
            p.missed_goals,
            p.different_goals,
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer