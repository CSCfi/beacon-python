from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import csv


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/kakeinan/beacon-python/beacon_api/example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Beacon_dataset_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stable_id = db.Column(db.String(50))
    description = db.Column(db.String(800))
    access_type = db.Column(db.String(50))
    reference_genome = db.Column(db.String(50))
    variant_cnt = db.Column(db.Integer)
    call_cnt = db.Column(db.Integer)
    sample_cnt = db.Column(db.Integer)
    dataset_rows = db.relationship('Beacon_data_table', backref='dataset') # list with all the rows from the dataset

class Beacon_data_table(db.Model):
    __tablename__ = 'EGAD00000000028'
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('beacon_dataset_table.id'))
    start = db.Column(db.Integer)
    chromosome = db.Column(db.String(50))
    reference = db.Column(db.String(50))
    alternate = db.Column(db.String(50))
    end = db.Column(db.Integer)
    type = db.Column(db.String(50))
    sv_length = db.Column(db.Integer)
    variant_cnt = db.Column(db.Integer)
    call_cnt = db.Column(db.Integer)
    sample_cnt = db.Column(db.Integer)
    frequency = db.Column(db.Integer)



def load_dataset_table():
    add_new = Beacon_dataset_table(stable_id='EGAD00000000028',description= 'Sample variants',access_type= 'PUBLIC',reference_genome= 'grch37',variant_cnt= '74',call_cnt= '74',sample_cnt= '1')
    db.session.add(add_new)
    db.session.commit()

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
        yield buffer[:idx]


def load_data_table(filename):
    rows = 0
    csvData = csv.reader(open('./beacon_api/{}'.format(filename), "r"), delimiter=";")
    dataset = Beacon_dataset_table.query.filter_by(id=1).first()
    divData = chunks(csvData)  # divide into 10000 rows each

    for chunk in divData:
        for dataset_id, start, chromosome, reference, alternate, end, type, sv_length, variant_cnt, call_cnt, sample_cnt, frequency in chunk:
            add_new = Beacon_data_table(dataset=dataset, start=start, chromosome=chromosome, reference=reference,
                                        alternate=alternate, \
                                        end=end, type=type, sv_length=sv_length, variant_cnt=variant_cnt, call_cnt=call_cnt, sample_cnt=sample_cnt, frequency=frequency)
        db.session.add(add_new)
        db.session.commit()
        rows += 10000
        print(rows)

#def load_data_table(filename):
#    file = open('./beacon_api/{}'.format(filename), 'r')
#    dataset = Beacon_dataset_table.query.filter_by(id=1).first()
#    i = 0
#    while file:
#        str = file.readline().rstrip()
#        dataset_id, start, chromosome, reference, alternate, end, type, sv_length, variant_cnt, call_cnt, sample_cnt, frequency = str.split(";")
#        add_new = Beacon_data_table(dataset=dataset, start=start, chromosome=chromosome, reference=reference, alternate=alternate, \
#                         end=end, type=type, sv_length=sv_length, variant_cnt=variant_cnt, call_cnt=call_cnt, sample_cnt=sample_cnt, frequency=frequency)
#        db.session.add(add_new)
#        db.session.commit()
#        i += 1
#        if i % 1000 == 0:
#            print(i)

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
            "id": row_obj.stable_id,
            "name": None,
            "description": "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland.",
            "assemblyId": row_obj.reference_genome,
            "createDateTime": None,
            "updateDateTime": None,
            "version": None,
            "variantCount": row_obj.variant_cnt,
            "callCount": row_obj.call_cnt,
            "sampleCount": row_obj.sample_cnt,
            "externalUrl": None,
            "info": {
                "accessType": row_obj.access_type,
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
