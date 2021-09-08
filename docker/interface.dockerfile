FROM python:3.9.7-slim-bullseye

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY /requirements.txt requirements.txt

RUN pip install -r /requirements.txt