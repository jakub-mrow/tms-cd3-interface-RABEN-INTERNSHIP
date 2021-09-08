FROM python:3.9.7-slim-bullseye

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY /tmp/requirements.txt requirements.txt

RUN pip install -r /tmp/requirements.txt