#!/bin/bash
set -e

# ./restart.sh              — только бот для мьюта
# ./restart.sh tournament   — бот + база + сайт с таблицей

FILES="-f docker-compose.yml"
if [ "$1" = "tournament" ]; then
    FILES="-f docker-compose.yml -f docker-compose.tournament.yml"
fi

# гасим всё, что могло остаться от другого режима
docker compose -f docker-compose.yml -f docker-compose.tournament.yml down

docker compose $FILES up -d --build
docker compose $FILES logs -f
