FROM python:3.6-alpine3.8 as BUILD

RUN apk add --update \
    && apk add --no-cache build-base curl-dev linux-headers bash git\
    && apk add --no-cache libressl-dev libffi-dev\
    && rm -rf /var/cache/apk/*

COPY requirements.txt /root/beacon/requirements.txt
COPY setup.py /root/beacon/setup.py
COPY beacon_api /root/beacon/beacon_api

RUN pip install --upgrade pip && \
    pip install -r /root/beacon/requirements.txt && \
    pip install /root/beacon

FROM python:3.6-alpine3.8

RUN apk add --no-cache --update bash

LABEL maintainer "CSC Developers"
LABEL org.label-schema.schema-version="1.3"
LABEL org.label-schema.vcs-url="https://github.com/CSCFI/beacon-python"

COPY --from=BUILD usr/local/lib/python3.6/ usr/local/lib/python3.6/

COPY --from=BUILD /usr/local/bin/gunicorn /usr/local/bin/

COPY --from=BUILD /usr/local/bin/beacon /usr/local/bin/

COPY --from=BUILD /usr/local/bin/beacon_init /usr/local/bin/

RUN mkdir -p /app

WORKDIR /app

COPY ./deploy/app.sh /app/app.sh

RUN chmod +x /app/app.sh

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
