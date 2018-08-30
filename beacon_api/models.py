import csv
import datetime
from wsgi import db


# NOTE: if beacon_dataset_table is not filled the query wont know about the right datasets.


class Beacon_dataset_table(db.Model):
    """The `Beacon_dataset_table class` inherits the Model class from SQLAlchemy and creates the schema for the table `beacon_dataset_table`."""
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


class Beacon_data_table(db.Model):
    """The `Beacon_data_table class` inherits the Model class from SQLAlchemy and creates the schema for the table `genomes`."""
    __tablename__ = 'genomes'
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.String(200))
    start = db.Column(db.Integer)
    chromosome = db.Column(db.String(100))
    reference = db.Column(db.String(200))
    alternate = db.Column(db.String(200))
    end = db.Column(db.Integer)
    type = db.Column(db.String(100))
    sv_length = db.Column(db.Integer)
    variantCount = db.Column(db.Integer)
    callCount = db.Column(db.Integer)
    sampleCount = db.Column(db.Integer)
    frequency = db.Column(db.Float)


def load_dataset_table(name=None, description=None, assemblyId=None, version=None, variantCount=None, callCount=None, sampleCount=None, externalUrl=None,
                       accessType=None):
    """
    The `load_dataset_table()` function loads the data set table to the database. This table gives the user meta-data on the data sets.

    :type name: String
    :param name: Name of the data set that will be loaded into the database.
    :type description: String
    :param description: A short description of the data set.
    :type assemblyId: String
    :param assemblyId: Assembly identifier used in the data set.
    :type version: String
    :param version: Version of the data set.
    :type variantCount: Integer
    :param variantCount: The variant count for the whole data set.
    :type callCount: Integer
    :param callCount: The call count for the whole data set.
    :type sampleCount: Integer
    :param sampleCount: The number of samples in the data set.
    :type externalUrl: String
    :param externalUrl: An external Url for the data set.
    :type accessType: String
    :param accessType: The access type for the data set. can be "PUBLIC", "REGISTERED" or "CONTROLLED"
    """
    addNew = Beacon_dataset_table(name=name, description=description, assemblyId=assemblyId, version=version, variantCount=variantCount, callCount=callCount,
                                  sampleCount=sampleCount, externalUrl=externalUrl, accessType=accessType)
    db.session.add(addNew)
    db.session.commit()


def chunks(data, n=10000):
    """
    The `chunk()` function divides the data into chunks with 10000 rows each. It yieldes them as e generator to make the process more efficient.

    :type data: File
    :param data: A file handler to a .csv file containing the data.
    :type n: Integer
    :param n: The number of rows.
    :type buffer: Generator
    :yield buffer:
    """
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
        yield buffer[:idx]  # if there is less than 10000 rows left it yields the rest


def load_data_table(filename):
    """
    The `load_data_table()` function loads all the data from the given file into the table. Because of the big amount of
    rows in the files the function uses the `chunk()` function to divide the rows into 10000 row chunks witch it commits in chunks.
    This is because it takes significantly less time to commit them as 10000 row chunks than row by row.

    :type filename: String
    :param filename: The path of the file.
    """
    rows = 0
    csvData = csv.reader(open('{}'.format(filename), "r"), delimiter=";")
    divData = chunks(csvData)  # divide into 10000 rows each

    for chunk in divData:
        for dataset_id, start, chromosome, reference, alternate, end, type, sv_length, variantCount, callCount, sampleCount, frequency in chunk:
            addNew = Beacon_data_table(dataset_id=dataset_id, start=start, chromosome=chromosome, reference=reference, alternate=alternate, end=end, type=type,
                                       sv_length=sv_length, variantCount=variantCount, callCount=callCount, sampleCount=sampleCount, frequency=frequency)
            db.session.add(addNew)
        db.session.commit()
        rows += 10000
        print(rows)
