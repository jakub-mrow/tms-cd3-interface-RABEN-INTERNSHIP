FROM python:3.9.7-slim-bullseye

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=/app/api/main.py

COPY docker/requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

LABEL maintainer bzwi2
LABEL Project=tms-cd3-interface
