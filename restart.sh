#!/bin/bash
docker compose down
docker compose up -d --build
export $(cat .env.local | grep -v ^# | xargs) && alembic upgrade head
docker compose logs -f
