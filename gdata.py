from requests import get, post
from json import loads, dumps
from base64 import b64decode
from dbms import query,update,Jsons
from time import time
from traceback import format_exc
import os

headers_common = None
params_common = None
gpinfo = None

def get_gpinfo():
    try:
        from_db = loads(query(Jsons,'gpinfo')[0])
        return from_db
    except:
        print(format_exc())
        return {}

def init(force = False):
    global headers_common, params_common, gpinfo
    if(not gpinfo):
        gpinfo = get_gpinfo()
    if(force or not headers_common):
        headers_common = {
            'Accept-Language': 'en',
            'Vary': 'Accept-Language',
            'Authorization': 'Bearer '+ gpinfo['access_token'],
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate'
        }
    if(force or not params_common):
        params_common = {
            'hash': gpinfo['hash'],
            'lang':'en',
            'id': gpinfo['id']
        }

def update_tokens():
    headers = {
        'Cache-Control': 'no-cache',
        'User-Agent': 'Android/22 MyGP/166 (en)'
    }
    headers.update(headers_common)
    json_ = {'refresh_token': gpinfo['refresh_token']}

    res = post('https://mygp.grameenphone.com/mygpapi/v2/oauth/connectid/refresh-token/android', headers=headers, json=json_, params=params_common)
    
    if(res.status_code == 200):
        json_ = res.json()
        try:
            _ = json_['error']
            print('Error: Token update failed.')
            print(res.text)
            return
        except:
            pass
        gpinfo.update(json_)
        
        result = update(Jsons,'gpinfo',dumps(gpinfo))
        if(result[1]==200):
            print('DB update successful.')
        else:
            print('DB update failed.')
    else:
        print('Token update failed. Code:', res.status_code)
        print(res.text)

def validate_tokens():
    init()
    if(time()>float(gpinfo['expire_at'])):
        update_tokens()
        init(force=True)

def get_my_details():
    validate_tokens()
    headers_me = {
        'NOTFIRST': '1',
        'User-Agent': 'Android/22 MyGP/166 (en) ID/'+ gpinfo['me_ua'],
    }

    headers_me.update(headers_common)
    res = get('https://mygp.grameenphone.com/mygpapi/me',headers=headers_me,params=params_common).json()
    return res

def get_balance_raw():
    validate_tokens()
    headers_bal = {'User-Agent': 'Android/22 MyGP/166 (en)'}
    headers_bal.update(headers_common)
    res = get('https://mygp.grameenphone.com/mygpapi/balance',headers=headers_bal,params=params_common).json()
    return res

def get_formated_data_bal():
    try:
        raw_bal = get_balance_raw()
        total = raw_bal['internet_details']
        msg = 'Total Balance: '+total['value'] + ' ' + total['unit']

        for p in raw_bal['internet_packs']:
            m = '\n\nPack: {}\n'.format(p['name']) + \
                'Remaining: {}\n'.format(p['value']) + \
                'Validity: {}'.format(p['remaining'])
            msg += m

        return msg
    except:
        print(format_exc())
        return 'Something went wrong.\n\n' + str(raw_bal)
