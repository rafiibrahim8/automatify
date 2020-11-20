from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Jsons(db.Model):
    sl = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    jdata = db.Column(db.String, unique=False, nullable=False)

