import re

def parse_results(text: str):
    results = []
    errors = []

    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        is_extra_time = bool(re.search(r'\bот\b', line, re.IGNORECASE))
        line = re.sub(r'\bот\b', '', line, flags=re.IGNORECASE).strip()

        pattern = r'^(.+?)\s*-\s*(.+?)\s+(\d+)\s*-\s*(\d+)$'
        match = re.match(pattern, line)

        if not match:
            errors.append(line)
            continue

        player1 = match.group(1).strip().lower()
        player2 = match.group(2).strip().lower()
        score1 = int(match.group(3))
        score2 = int(match.group(4))

        results.append((player1, player2, score1, score2, is_extra_time))

    return results, errors