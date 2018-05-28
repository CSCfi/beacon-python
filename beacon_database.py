from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from beacon_flask_api import db
#app = Flask(__name__)


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


def load_data_table():
    file = open('EGAD00000000028.SNPs.txt', 'r')
    dataset = Beacon_dataset_table.query.filter_by(id=1).first()
    while file:
        str = file.readline().rstrip()
        dataset_id, start, chromosome, reference, alternate, end, type, sv_length, variant_cnt, call_cnt, sample_cnt, frequency = str.split(";")
        add_new = Beacon_data_table(dataset=dataset, start=start, chromosome=chromosome, reference=reference, alternate=alternate, \
                         end=end, type=type, sv_length=sv_length, variant_cnt=variant_cnt, call_cnt=call_cnt, sample_cnt=sample_cnt, frequency=frequency)
        db.session.add(add_new)
        db.session.commit()

