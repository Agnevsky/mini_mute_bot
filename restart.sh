#!/bin/bash
docker-compose down
docker-compose up -d --build
docker-compose exec bot alembic upgrade head
docker-compose logs -f
