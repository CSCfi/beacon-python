#!/bin/bash

LOCALDIR="/app/data"
REGEX="ALL\.chr.*\.vcf\.gz$"
REMOTEDIR="/vol1/ftp/release/20130502/"

cd $LOCALDIR
ls -al
lftp ftp://ftp.1000genomes.ebi.ac.uk << EOF
    cd $REMOTEDIR
    mirror --only-missing -v -r -P 3 -i $REGEX
EOF

cd ..
for file in /app/data/*
do
  beacon_init "$file" "/app/example_metadata.json"
done
