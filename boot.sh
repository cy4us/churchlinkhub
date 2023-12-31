#!/bin/bash

# Übernommen und z.T. angepasst
source venv/bin/activate
while true; do
    flask db migrate
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done
exec gunicorn -w 4 --bind 0.0.0.0:5000 wsgi:app
