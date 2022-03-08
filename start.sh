#!/bin/sh
python3 run_gunicorn.py --bind localhost:5000 wsgi:app
