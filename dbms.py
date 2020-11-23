from flask_sqlalchemy import SQLAlchemy

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

def update(table,name,content):
    if(table.lower() == 'jsons'):
        with app_.app_context():
            result = Jsons.query.filter_by(name=name).first()
            if(not result):
                db.session.add(Jsons(name=name, jdata=content))
            else:
                result.jdata = content
            db.session.commit()
    else:
        return 'Bad table name', 400
    
    return 'OK', 200

def query(table,name):
    if(table.lower() == 'jsons'):
        with app_.app_context():
            result = Jsons.query.filter_by(name=name).first()
            if(not result):
                'Name not found', 404
            else:
                return result.jdata, 200
    else:
        return 'Bad table name', 400
