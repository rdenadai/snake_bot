#!/bin/bash

cd /code

python -m snake_bot.database.start_db

if [ "$MODE" = "development" ]; then
    pip install debugpy -t /tmp && python /tmp/debugpy --wait-for-client --listen 0.0.0.0:5678 -m snake_bot.main
elif [ "$MODE" = "production" ]; then
    python -m snake_bot.main
fi
