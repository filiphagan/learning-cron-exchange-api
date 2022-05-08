# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine

WORKDIR /code
ARG freq=10800
ARG cache=7

COPY main.py requirements.txt entrypoint.sh backup.sh .

RUN apk --update add restic; \
    pip install -r requirements.txt

ENV RESTIC_REPOSITORY=/backups
ENV RESTIC_PASSWORD=ThisIsNotASecret

RUN mkdir -p /code/outputs /backups && \
    chmod +x /code/main.py /code/backup.sh

# Call API every 3h, backup every 12h
RUN echo "0 */3 * * * /code/main.py --cache=$cache" >> /etc/crontabs/root; \
    echo "0 */12 * * * /code/backup.sh" >> /etc/crontabs/root

ENTRYPOINT ["/code/entrypoint.sh"]