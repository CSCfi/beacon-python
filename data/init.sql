CREATE TABLE IF NOT EXISTS beacon_dataset_table (
    id SERIAL,
    name VARCHAR(50),
    dataset_id VARCHAR(200),
    description VARCHAR(800),
    assemblyId VARCHAR(20),
    createDateTime TIMESTAMPTZ,
    updateDateTime TIMESTAMPTZ,
    "version" VARCHAR(5),
    sampleCount INTEGER,
    externalUrl VARCHAR(50),
    accessType VARCHAR(10),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS beacon_data_table (
    id SERIAL,
    dataset_id VARCHAR(200),
    start INTEGER,
    chromosome VARCHAR(2),
    reference VARCHAR(200),
    alternate VARCHAR(200),
    "end" INTEGER,
    type VARCHAR(100),
    sv_length INTEGER,
    variantCount INTEGER,
    callCount INTEGER,
    sampleCount INTEGER,
    frequency REAL,
    PRIMARY KEY (id)
);

CREATE OR REPLACE VIEW dataset_metadata(name, dataset_id, description, assemblyId, createDateTime, updateDateTime, version, variantCount, callCount, sampleCount, externalUrl, accessType)
AS SELECT a.name, a.dataset_id, a.description, a.assemblyId, a.createDateTime, a.updateDateTime, a.version, SUM(b.variantCount), SUM(b.callCount), a.sampleCount, a.externalUrl, a.accessType
FROM beacon_dataset_table a, beacon_data_table b
WHERE a.dataset_id=b.dataset_id
GROUP BY a.name, a.dataset_id, a.description, a.assemblyId, a.createDateTime, a.updateDateTime, a.version, a.sampleCount, a.externalUrl, a.accessType;