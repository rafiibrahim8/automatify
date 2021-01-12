from flask_mongoengine import MongoEngine
import os

db = MongoEngine()
app_ = None

class PubKeys(db.Document):
    user = db.StringField(unique=True, required=True)
    field = db.StringField(required=False, unique_with='user')
    data = db.StringField(unique=True, required=True)

class Users(db.Document):
    user = db.StringField(unique=False, required=True)
    field = db.StringField(required=True, unique_with='user')
    data = db.DictField(required=True)

def add_db(app):
    global app_
    app_ = app
    db.init_app(app_)

def update(cls, field, content, user):
    user = user.lower()
    if(not isinstance(content, dict)):
        content = {os.environ['DB_X_SECRET']: content}
    with app_.app_context():
        document = cls.objects(field=field, user=user).first()
        if(not document):
            document = cls(user=user, field=field, data=content)
        else:
            document.data = content
        document.save()
    return 'OK', 200

def query(cls,field,user):
    user = user.lower()
    with app_.app_context():
        document = cls.objects(field=field, user=user).first()
        if(not document or not document.data):
            return 'Not found', 404
        elif(len(document.data) ==1 and document.data.get(os.environ['DB_X_SECRET'])):
            return document.data.get(os.environ['DB_X_SECRET']), 200
        else:
            return document.data, 200

def querys(table,field,user):
    q = query(table,field,user)
    return q[0] if(q[1]==200) else None

def get_pbkey(user):
    user = user.lower()
    with app_.app_context():
        document = PubKeys.objects(user=user).first()
        if(not document or not document.key_b64):
            return 'Not found', 404
        else:
            return document.key_b64, 200

def delete_all(user):
    user = user.lower()
    with app_.app_context():
        documents = Users.objects(user=user)
        if(not documents):
            return 'Not found', 404
        else:
            for i in documents:
                i.delete()
        return 'OK', 200

def delete_field(user, field, cls=Users):
    user = user.lower()
    with app_.app_context():
        document = cls.objects(user=user, field=field).first()
        if(not document):
            return 'Not found', 404
        else:
            document.delete()
        return 'OK', 200

def delete_self(user):
    user = user.lower()
    delete_all(user)
    return delete_field(user,'key_b64', PubKeys)

def get_type(table):
    available_tables = {
        'field' : Users,
        'key' : PubKeys
    }
    return available_tables.get(table)

def map_fbid_to_user(fbid):
    with app_.app_context():
        document = Users.objects(field='fbid',data={os.environ['DB_X_SECRET']: fbid}).first()
        if(not document):
            return None
        else:
            return document.user
