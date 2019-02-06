FROM python:3.6-alpine3.8

LABEL maintainer "CSC Developers"

RUN apk add --update \
    && apk add --no-cache build-base curl-dev linux-headers bash git\
    && apk add --no-cache libressl-dev libffi-dev\
    && apk add --no-cache supervisor \
    && rm -rf /var/cache/apk/*

RUN pip install -r https://raw.githubusercontent.com/CSCfi/beacon-python/master/requirements.txt
RUN pip install git+https://github.com/CSCfi/beacon-python.git@master

RUN mkdir -p /app

WORKDIR /app

COPY app.sh /app/app.sh

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
