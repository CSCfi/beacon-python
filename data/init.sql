CREATE TABLE IF NOT EXISTS beacon_dataset_table (
    id SERIAL,
    name VARCHAR(50),
    dataset_id VARCHAR(200),
    description VARCHAR(800),
    assemblyId VARCHAR(20),
    createDateTime TIMESTAMPTZ,
    updateDateTime TIMESTAMPTZ,
    version VARCHAR(5),
    variantCount INTEGER,
    callCount INTEGER,
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
    PRIMARY KEY (id),
    FOREIGN KEY (dataset_id) REFERENCES beacon_dataset_table (dataset_id)
);
