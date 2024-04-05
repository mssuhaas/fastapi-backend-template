#!/bin/bash

if [[ $1 == "--test" ]]; then
    uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug --reload
else
    gunicorn main:app --workers=4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
fi