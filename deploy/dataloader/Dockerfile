FROM cscfi/beacon-python

RUN apk add --no-cache --update curl-dev lftp

RUN wget https://raw.githubusercontent.com/CSCfi/beacon-python/master/data/example_metadata.json
RUN wget https://raw.githubusercontent.com/CSCfi/beacon-python/master/data/init.sql

COPY dataloader.sh /app/dataloader.sh

RUN chgrp -R 0 /app && \
    chmod -R g=u /app

ENTRYPOINT ["/bin/sh", "-c", "/app/dataloader.sh"]
