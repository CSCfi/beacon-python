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
    accessType VARCHAR(10),
    PRIMARY KEY (index)
);

CREATE TABLE IF NOT EXISTS beacon_data_table (
    index SERIAL,
    datasetId VARCHAR(128),
    start INTEGER,
    chromosome VARCHAR(2),
    reference VARCHAR(8192),
    alternate VARCHAR(8192),
    "end" INTEGER,
    variantType VARCHAR(16),
    variantCount INTEGER,
    callCount INTEGER,
    frequency REAL,
    PRIMARY KEY (index)
);

CREATE OR REPLACE VIEW dataset_metadata(name, datasetId, description, assemblyId, createDateTime, updateDateTime, version, callCount, variantCount, sampleCount, externalUrl, accessType)
AS SELECT a.name, a.datasetId, a.description, a.assemblyId, a.createDateTime, a.updateDateTime, a.version, 0 as callCount, 0 as variantCount, a.sampleCount, a.externalUrl, a.accessType
FROM beacon_dataset_table a, beacon_data_table b
WHERE a.datasetId=b.datasetId
GROUP BY a.name, a.datasetId, a.description, a.assemblyId, a.createDateTime, a.updateDateTime, a.version, a.sampleCount, a.externalUrl, a.accessType;