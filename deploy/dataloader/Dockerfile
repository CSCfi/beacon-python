FROM python:3.6-alpine3.8

LABEL maintainer "CSC Developers"

RUN apk add --update \
    && apk add --no-cache build-base libressl-dev curl-dev linux-headers bash git libffi-dev\
    && apk add --no-cache py-setuptools lftp \
    && rm -rf /var/cache/apk/*

RUN pip install -r https://raw.githubusercontent.com/CSCfi/beacon-python/master/requirements.txt
RUN pip install git+https://github.com/CSCfi/beacon-python.git@master

RUN mkdir -p /app

RUN mkdir -p /app/data

WORKDIR /app

RUN wget https://raw.githubusercontent.com/CSCfi/beacon-python/master/data/example_metadata.json
RUN wget https://raw.githubusercontent.com/CSCfi/beacon-python/master/data/init.sql

COPY dataloader.sh /app/dataloader.sh

RUN chgrp -R 0 /app && \
    chmod -R g=u /app

ENTRYPOINT ["/bin/sh", "-c", "/app/dataloader.sh"]
