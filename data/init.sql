CREATE TYPE access_levels AS enum('CONTROLLED', 'REGISTERED', 'PUBLIC');

CREATE TABLE IF NOT EXISTS beacon_dataset_table (
    index SERIAL,
    name VARCHAR(128),
    datasetId VARCHAR(128),
    description VARCHAR(512),
    assemblyId VARCHAR(16),
    createDateTime TIMESTAMP WITH TIME ZONE,
    updateDateTime TIMESTAMP WITH TIME ZONE,
    version VARCHAR(8),
    sampleCount INTEGER,
    externalUrl VARCHAR(256),
    accessType access_levels,
    PRIMARY KEY (index)
);

/*
The values in this table take a long time to compute on large datasets
Most likely these values do not change once the dataset is loaded so one
could compute the values and UPDATE the table once the all dataset is inserted

callcount: SELECT count(*) FROM (SELECT distinct(datasetId, chromosome, reference, start)
                                 FROM beacon_data_table) t;

variantcount: SELECT count(*) FROM beacon_data_table;
*/

CREATE TABLE IF NOT EXISTS beacon_dataset_counts_table (
    datasetId VARCHAR(128),
    callCount INTEGER DEFAULT NULL,
    variantCount BIGINT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS beacon_data_table (
    index SERIAL,
    datasetId VARCHAR(128),
    start INTEGER,
    chromosome VARCHAR(2),
    reference VARCHAR(8192),
    alternate VARCHAR(8192),
    "end" INTEGER,
    aggregatedVariantType VARCHAR(16),
    alleleCount INTEGER,
    callCount INTEGER,
    frequency REAL,
    variantType VARCHAR(16),
    PRIMARY KEY (index)
);

CREATE TABLE IF NOT EXISTS beacon_mate_table (
    index SERIAL,
    datasetId VARCHAR(128),
    chromosome VARCHAR(2), 
    chromosomeStart INTEGER,
    chromosomePos VARCHAR(128), /*for working with MATEID*/
    mate VARCHAR(2), 
    mateStart INTEGER,
    matePos VARCHAR(128), /*for working with MATEID*/
    reference VARCHAR(8192),
    alternate VARCHAR(8192),
    alleleCount INTEGER,
    callCount INTEGER,
    frequency REAL,
    "end" INTEGER,
    PRIMARY KEY (index)
);

CREATE UNIQUE INDEX data_conflict ON beacon_data_table (datasetId, chromosome, start, reference, alternate);
CREATE UNIQUE INDEX metadata_conflict ON beacon_dataset_table (name, datasetId);
CREATE UNIQUE INDEX mate_conflict ON beacon_mate_table (datasetId, chromosome, mate, chromosomePos, matePos);


CREATE OR REPLACE VIEW dataset_metadata(name, datasetId, description, assemblyId,
                                        createDateTime, updateDateTime, version,
                                        callCount, variantCount, sampleCount, externalUrl, accessType)
AS SELECT a.name, a.datasetId, a.description, a.assemblyId, a.createDateTime,
          a.updateDateTime, a.version, b.callCount,
          b.variantCount,
          a.sampleCount, a.externalUrl, a.accessType
FROM beacon_dataset_table a, beacon_dataset_counts_table b
WHERE a.datasetId=b.datasetId
GROUP BY a.name, a.datasetId, a.description, a.assemblyId, a.createDateTime,
         a.updateDateTime, a.version, a.sampleCount, a.externalUrl, a.accessType, b.callCount, b.variantCount;
