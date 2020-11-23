from flask_sqlalchemy import SQLAlchemy
from json import dumps

db = SQLAlchemy()

class Jsons(db.Model):
    sl = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    jdata = db.Column(db.String, unique=False, nullable=False)

def get_db(app=None):
    global db
    if(app==None):
        return db
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db

def update_db(command):
    try:
        table = command['table']
        name = command['name']
        content = command['content']
    except:
        return 'Not Enough Data', 400
    
    if(table.lower() == 'jsons'):
        result = Jsons.query.filter_by(name=name).first()
        if(not result):
            db.session.add(Jsons(name=name, jdata=dumps(content)))
        else:
            result.jdata = dumps(content)
        db.session.commit()
    else:
        return 'Bad table name', 400
    
    return 'OK', 200


