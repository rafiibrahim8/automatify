from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from base64 import b64decode
from dbms import update, get_type, get_pbkey, delete_self, delete_all, delete_field
from service_handler import get_service
from json import loads
import os
import time
from traceback import print_exc

TIME_THRESHOLD = 10

def resolve_crypto(jdata):
    try:
        if(jdata.get('admin', False)):
            public_key = RSA.import_key(b64decode(os.environ['PUBLIC_KEY']))
        else:
            public_key = RSA.import_key(b64decode(get_pbkey(jdata['user'].lower())))
    except:
        return 'Invalid User', 403
    try:
        verifier = PKCS1_v1_5.new(public_key)
        digest = SHA256.new(jdata['body'].encode('utf-8'))
        auth = verifier.verify(digest, b64decode(jdata['sig']))
    except:
        print_exc()
        return 'Bad request', 400
    if(not auth):
        return "Key verification failed.", 403
    try:
        body = loads(b64decode(jdata['body']))
        t = abs(int(body.get('time',0)))
        if(int(time.time()) - t < TIME_THRESHOLD):
            return body, 200
        else:
            return 'Time not in sync', 403
    except:
        pass
    return 'Bad request', 400

def update_h(jdata):
    cryp_r = resolve_crypto(jdata)
    if(cryp_r[1] != 200):
        return cryp_r
    body = cryp_r[0]
    try:
        user = jdata['user']
        u_type = body['type']
        u_data = body['data']
        if(u_type not in ['key','field']):
            return 'Bad Request', 400
        if(u_type == 'field'):
            field = body['field']
        else:
            field = 'key_b64'
        assert field not in ['self', 'all']
    except:
        return 'Bad Request', 400
    
    return update(get_type(u_type), field, u_data, user)

def delete_h(jdata):
    cryp_r = resolve_crypto(jdata)
    if(cryp_r[1] != 200):
        return cryp_r
    body = cryp_r[0]
    try:
        sig = jdata['sig']
        user = jdata['user']
        delete = body['delete']
    except:
        return 'Not Enough Data', 400

    switch = {
        'self': delete_self,
        'all': delete_all
    }
    switch_r = switch.get(delete)
    if(switch_r):
        return switch_r(user)
    return delete_field(user, delete)

def get_info(user, service):
    service_ = get_service(service)
    if(service_):
        return service_(user)
    return 'Service {} not found'.format(service), 404

def info_h(jdata):
    cryp_r = resolve_crypto(jdata)
    if(cryp_r[1] != 200):
        return cryp_r
    body = cryp_r[0]
    try:
        user = jdata['user']
        service = body['service']
    except:
        return 'Bad Request', 400

    return get_info(user, service)
