#!/bin/bash
flask db upgrade
gunicorn run:app --bind 0.0.0.0:10000