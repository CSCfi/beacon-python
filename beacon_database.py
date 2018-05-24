from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/kakeinan/beacon-python/example.db'
db = SQLAlchemy(app)

class Beacon_data_table(db.Model):
    __tablename__ = 'EGAD00000000028'
    id = db.Column(db.String(10),primary_key=True)
    dataset_id = db.Column(db.String(10))
    start = db.Column(db.String(50))
    chromosome = db.Column(db.String(50))
    reference = db.Column(db.String(50))
    alternate = db.Column(db.String(50))
    end = db.Column(db.String(50))
    type = db.Column(db.String(50))
    sv_length = db.Column(db.String(50))
    variant_cnt = db.Column(db.String(50))
    call_cnt = db.Column(db.String(50))
    sample_cnt = db.Column(db.String(50))
    frequency = db.Column(db.String(50))

class Beacon_dataset_table(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    stable_id = db.Column(db.String(50))
    description = db.Column(db.String(800))
    access_type = db.Column(db.String(50))
    reference_genome = db.Column(db.String(50))
    variant_cnt = db.Column(db.String(50))
    call_cnt = db.Column(db.String(50))
    sample_cnt = db.Column(db.String(50))


def load_data_table():
    file = open('EGAD00000000028.SNPs.txt', 'r')
    i = 1
    while file:
        str = file.readline().rstrip()
        dataset_id, start, chromosome, reference, alternate, end, type, sv_length, variant_cnt, call_cnt, sample_cnt, frequency = str.split(";")
        add_new = Beacon_data_table(id=i, dataset_id=dataset_id, start=start, chromosome=chromosome, reference=reference, alternate=alternate, \
                         end=end, type=type, sv_length=sv_length, variant_cnt=variant_cnt, call_cnt=call_cnt, sample_cnt=sample_cnt, frequency=frequency)
        db.session.add(add_new)
        db.session.commit()
        i += 1

def load_dataset_table():
    add_new = Beacon_dataset_table(id=1 ,stable_id= 'EGAD00000000028',description= 'Sample variants',access_type= 'PUBLIC',reference_genome= 'grch37',variant_cnt= '74',call_cnt= '74',sample_cnt= '1')
    db.session.add(add_new)
    db.session.commit()