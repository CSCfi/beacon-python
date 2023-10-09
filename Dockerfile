FROM python:3.12.0-slim as BUILD

RUN apt-get update \
    && apt-get install -y build-essential bash git gcc \
    && apt-get install -y zlib1g-dev liblzma-dev libcurl4-gnutls-dev libssl-dev libffi-dev autoconf libbz2-dev xz-utils \
    && apt-get install -y python3-dev libdeflate-dev libncurses5-dev libncursesw5-dev libreadline-dev

COPY requirements.txt /root/beacon/requirements.txt

ENV CYTHONIZE=1
# the following related to https://github.com/brentp/cyvcf2/issues/240#issuecomment-1534257675
ENV LIBDEFLATE=1

RUN pip install --upgrade pip \
    && pip install -r /root/beacon/requirements.txt

COPY setup.py /root/beacon/setup.py
COPY beacon_api /root/beacon/beacon_api
RUN pip install /root/beacon

FROM python:3.12.0-slim

RUN apt-get install -y bash

LABEL maintainer "CSC Developers"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.vcs-url="https://github.com/CSCFI/beacon-python"

RUN apt-get update \
    && apt-get install -y curl bzip2 xz-utils

COPY --from=BUILD usr/local/lib/python3.10/ usr/local/lib/python3.10/

COPY --from=BUILD /usr/local/bin/gunicorn /usr/local/bin/

COPY --from=BUILD /usr/local/bin/beacon /usr/local/bin/

COPY --from=BUILD /usr/local/bin/beacon_init /usr/local/bin/

RUN mkdir -p /app

WORKDIR /app

COPY ./deploy/app.sh /app/app.sh

RUN chmod +x /app/app.sh

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
