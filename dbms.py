from flask_sqlalchemy import SQLAlchemy
from json import dumps

db = SQLAlchemy()
app_ = None

class Jsons(db.Model):
    sl = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    jdata = db.Column(db.String, unique=False, nullable=False)

def add_db(app):
    global app_
    app_ = app
    db.init_app(app_)
    with app_.app_context():
        db.create_all()

def update(cls,name,content):
    if(not isinstance(content,str)):
        content = dumps(content)
    with app_.app_context():
        result = cls.query.filter_by(name=name).first()
        if(not result):
            db.session.add(cls(name=name, jdata=content))
        else:
            result.jdata = content
        db.session.commit()
    return 'OK', 200

def query(cls,name):
    with app_.app_context():
        result = cls.query.filter_by(name=name).first()
        if(not result or not result.jdata):
            return 'Not found', 404
        else:
            return result.jdata, 200

def querys(table,name):
    q = query(table,name)
    return q[0] if(q[1]==200) else None

def get_table(table):
    available_tables = {
        'jsons' : Jsons
    }
    return available_tables.get(table)
