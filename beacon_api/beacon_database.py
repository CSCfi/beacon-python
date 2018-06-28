from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import csv, datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/kakeinan/beacon-python/beacon_api/beaconDatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# NOTE: if beacon_dataset_table is not filled the query wont know about tthe right datasets.

class Beacon_dataset_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(800))
    assemblyId = db.Column(db.String(20))
    createDateTime = db.Column(db.DateTime, default=datetime.date.today())
    updateDateTime = db.Column(db.DateTime)
    version = db.Column(db.String(5))
    variantCount = db.Column(db.Integer)
    callCount = db.Column(db.Integer)
    sampleCount = db.Column(db.Integer)
    externalUrl = db.Column(db.String(50))
    accessType = db.Column(db.String(10))
    authorized = db.Column(db.String(10))

    dataset_rows = db.relationship('Beacon_data_table', backref='dataset') # list with all the rows from the dataset

class Beacon_data_table(db.Model):
    __tablename__ = 'genomes'
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('beacon_dataset_table.id'))
    start = db.Column(db.Integer)
    chromosome = db.Column(db.String(50))
    reference = db.Column(db.String(50))
    alternate = db.Column(db.String(50))
    end = db.Column(db.Integer)
    type = db.Column(db.String(50))
    sv_length = db.Column(db.Integer)
    variantCount = db.Column(db.Integer)
    callCount = db.Column(db.Integer)
    sampleCount = db.Column(db.Integer)
    frequency = db.Column(db.Integer)


# The load dataset_table() function loads the dataset table to the database. This table gives the user meta-data on the datasets
def load_dataset_table(name=None, description=None, assemblyId=None, version=None, variantCount=None, callCount=None, sampleCount=None, externalUrl=None, accessType=None, authorized=None):
    add_new = Beacon_dataset_table(name=name, description=description, assemblyId=assemblyId, version=version, variantCount=variantCount, callCount=callCount, sampleCount=sampleCount, externalUrl=externalUrl, accessType=accessType, authorized=authorized)
    db.session.add(add_new)
    db.session.commit()

# The chunk() function divides the data into chunks with 10000 rows each. It yieldes them as e generator to make the process more efficient.
def chunks(data, n=10000):
    buffer = [None] * n
    idx = 0
    for record in data:
        buffer[idx] = record
        idx += 1
        if idx == n:
            yield buffer
            buffer = [None] * n
            idx = 0
    if idx > 0:
        yield buffer[:idx] # if there is less than 10000 rows left it yields the rest

# The load_data_table() function loads all the data from the given file into the database. Because of the big amount of
# rows in the files the function uses the chunk() funktion to divede the rows into 10000 row chunks witch it commits in chunks.
# This is because it takes significantly less time to commit them as 10000 row chunks than row by row.
def load_data_table(filename):
    rows = 0
    csvData = csv.reader(open('./beacon_api/{}'.format(filename), "r"), delimiter=";")
    dataset = Beacon_dataset_table.query.filter_by(id=1).first()
    divData = chunks(csvData)  # divide into 10000 rows each

    for chunk in divData:
        for dataset_id, start, chromosome, reference, alternate, end, type, sv_length, variantCount, callCount, sampleCount, frequency in chunk:
            add_new = Beacon_data_table(dataset=dataset, start=start, chromosome=chromosome, reference=reference,
                                        alternate=alternate, \
                                        end=end, type=type, sv_length=sv_length, variantCount=variantCount, callCount=callCount, sampleCount=sampleCount, frequency=frequency)
            db.session.add(add_new)
        db.session.commit()
        rows += 10000
        print(rows)


def constructor():

    BeaconAllelRequest = [{
        "alternateBases": "A",
        "referenceBases": "C",
        "referenceName": "17",
        "start": 6689,
        "assemblyId": "GRCh37",
        "datasetIds": None,
        "includeDatasetResponses": False
    },
    {
        "alternateBases": "G",
        "referenceBases": "A",
        "referenceName": "1",
        "start": 14929,
        "assemblyId": "GRCh37",
        "datasetIds": [
        "EGAD00000000028"
        ],
        "includeDatasetResponses": "ALL"
    },
    {
        "alternateBases": "CCCCT",
        "referenceBases": "C",
        "referenceName": "1",
        "start": 866510,
        "assemblyId": "GRCh37",
        "datasetIds": [
        "EGAD00001000740",
        "EGAD00001000741"
        ],
        "includeDatasetResponses": "HIT"
    }
    ]

    BeaconDataset = []
    db_object = Beacon_dataset_table
    db_table = db_object.query.all() # List of all the rows in the beacon_dataset_table
    for row_obj in db_table:
        asd = {
            "id": row_obj.id,
            "name": row_obj.name,
            "description": row_obj.description,
            "assemblyId": row_obj.assemblyId,
            "createDateTime": None,
            "updateDateTime": None,
            "version": None,
            "variantCount": row_obj.variantCount,
            "callCount": row_obj.callCount,
            "sampleCount": row_obj.sampleCount,
            "externalUrl": None,
            "info": {
                "accessType": row_obj.accessType,
                "authorized": "false"
            }
        }
        BeaconDataset.append(asd)

    Organization = {
        'id': 'EGA',
        'name': 'European Genome-Phenome Archive (EGA)',
        'description': 'The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.',
        'address': '',
        'welcomeUrl': 'https://ega-archive.org/',
        'contactUrl': 'mailto:beacon.ega@crg.eu',
        'logoUrl': 'https://ega-archive.org/images/logo.png',
        'info': None,
    }

    Beacon = {
        'id': 'ega-beacon',
        'name': 'EGA Beacon',
        'apiVersion': '0.4',
        'organization': Organization,
        'description': 'This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>',
        'version': 'v04',
        'welcomeUrl': 'https://ega-archive.org/beacon_web/',
        'alternativeUrl': 'https://ega-archive.org/beacon_web/',
        'createDateTime': '2015-06-15T00:00.000Z',
        'updateDateTime': None,
        'dataset': BeaconDataset,
        'sampleAlleleRequests': BeaconAllelRequest,
        'info': {
            "size": "60270153"
             }
    }
    return Beacon
