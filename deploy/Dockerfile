FROM python:3.6-alpine

LABEL maintainer "CSC Developers"

RUN apk add --update \
    && apk add --no-cache build-base libressl-dev curl-dev linux-headers bash git libffi-dev\
    && apk add --no-cache py-setuptools supervisor \
    && rm -rf /var/cache/apk/*

RUN pip install -r https://raw.githubusercontent.com/CSCfi/beacon-python/feature/aio/requirements.txt
RUN pip install git+https://github.com/CSCfi/beacon-python.git@feature/aio

RUN mkdir -p /app

WORKDIR /app

COPY app.sh /app/app.sh

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
