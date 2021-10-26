FROM python:3.9.7-slim-bullseye

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=/app/api/main.py

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

# Timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime
ENV TZ=Europe/Warsaw

LABEL maintainer bzwi2
LABEL Project=tms-cd3-api
