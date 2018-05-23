from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/kakeinan/beacon-python/example.db'
db = SQLAlchemy(app)

class Beacon(db.Model):
    __tablename__ = 'EGAD00000000028'
    id = db.Column('id', db.String,primary_key=True)
    dataset_id = db.Column('dataset_id', db.String)
    start = db.Column('start', db.String)
    chromosome = db.Column('chromosome', db.String)
    reference = db.Column('reference', db.String)
    alternate = db.Column('alternate', db.String)
    end = db.Column('end', db.String)
    type = db.Column('type', db.String)
    sv_length = db.Column('sv_length', db.String)
    variant_cnt = db.Column('variant_cnt', db.String)
    call_cnt = db.Column('call_cnt', db.String)
    sample_cnt = db.Column('sample_cnt', db.String)
    frequency = db.Column('frequency', db.String)



file = open('EGAD00000000028.SNPs.txt', 'r')
i = 1
while file:
    str = file.readline().rstrip()

    print(str)
    dataset_id, start, chromosome, reference, alternate, end, type, sv_length, variant_cnt, call_cnt, sample_cnt, frequency = str.split(";")
    add_new = Beacon(id=i, dataset_id=dataset_id, start=start, chromosome=chromosome, reference=reference, alternate=alternate, \
                     end=end, type=type, sv_length=sv_length, variant_cnt=variant_cnt, call_cnt=call_cnt, sample_cnt=sample_cnt, frequency=frequency)
    db.session.add(add_new)
    db.session.commit()
    i += 1
