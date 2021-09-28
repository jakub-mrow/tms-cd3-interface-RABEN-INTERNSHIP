FROM python:3.9.7-slim-bullseye

RUN apt-get update \
 && apt-get install -qqy \
    cron \
 && apt-get clean autoclean \
 && apt-get autoremove --yes \
 && rm -rf /var/lib/{apt,dpkg,cache,log}/ 

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

# Copy hello-cron file to the cron.d directory
COPY crontab /etc/cron.d/hello-cron
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/hello-cron
# Apply cron job
RUN crontab /etc/cron.d/hello-cron
# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime
ENV TZ=Europe/Warsaw

LABEL maintainer bzwi2
LABEL Project=tms-cd3-monitor