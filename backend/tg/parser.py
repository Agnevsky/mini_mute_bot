import re

def parse_result(text: str):
    """
    Парсит строки вида:
    Илья - Андрей 5 - 0
    Илья-Андрей 5-1
    илья-андрей 1-2 от
    
    Возвращает: (player1, player2, score1, score2, is_extra_time)
    """
    text = text.strip()
    
    # от = овертайм
    is_extra_time = bool(re.search(r'\bот\b', text, re.IGNORECASE))
    text = re.sub(r'\bот\b', '', text, flags=re.IGNORECASE).strip()

    # Разбиваем на части: имена и счёт
    # Паттерн: Имя1 - Имя2 счёт1 - счёт2
    pattern = r'^(.+?)\s*-\s*(.+?)\s+(\d+)\s*-\s*(\d+)$'
    match = re.match(pattern, text.strip())

    if not match:
        return None

    player1 = match.group(1).strip().lower()
    player2 = match.group(2).strip().lower()
    score1 = int(match.group(3))
    score2 = int(match.group(4))

    return player1, player2, score1, score2, is_extra_time