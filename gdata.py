from requests import get, post
from json import loads, dumps
from base64 import b64decode
from dbms import querys,update,Jsons
from time import time
from traceback import format_exc
import os

def get_gpinfo():
    try:
        from_db = loads(querys(Jsons,'gpinfo'))
        return from_db
    except:
        print(format_exc())
        return {}

def get_hp(type_, gpinfo=None):
    if(not gpinfo):
        gpinfo = get_gpinfo()
    if(type_.lower().startswith('h')):
        headers_common = {
                'Accept-Language': 'en',
                'Vary': 'Accept-Language',
                'Authorization': 'Bearer '+ gpinfo['access_token'],
                'Connection': 'close',
                'Accept-Encoding': 'gzip, deflate'
            }
        return headers_common
    
    elif(type_.lower().startswith('p')):
        params_common = {
            'hash': gpinfo['hash'],
            'lang':'en',
            'id': gpinfo['id']
        }
        return params_common
    else:
        raise TypeError('Must be headers or params.')

def update_tokens(gpinfo=None):
    if(not gpinfo):
        gpinfo = get_gpinfo()
    headers = {
        'Cache-Control': 'no-cache',
        'User-Agent': 'Android/22 MyGP/166 (en)'
    }
    headers.update(get_hp('h',gpinfo))
    json_ = {'refresh_token': gpinfo['refresh_token']}

    res = post('https://mygp.grameenphone.com/mygpapi/v2/oauth/connectid/refresh-token/android', headers=headers, json=json_, params=get_hp('p',gpinfo))
    
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

def validate_tokens(gpinfo=None):
    if(not gpinfo):
        gpinfo = get_gpinfo()
    if(time()>float(gpinfo['expire_at'])):
        update_tokens(gpinfo)

def get_my_details():
    gpinfo = get_gpinfo()
    validate_tokens(gpinfo)
    headers_me = {
        'NOTFIRST': '1',
        'User-Agent': 'Android/22 MyGP/166 (en) ID/'+ gpinfo['me_ua'],
    }

    headers_me.update(get_hp('h',gpinfo))
    res = get('https://mygp.grameenphone.com/mygpapi/me',headers=headers_me,params=get_hp('p',gpinfo)).json()
    return res

def get_balance_raw():
    gpinfo = get_gpinfo()
    validate_tokens(gpinfo)
    headers_bal = {'User-Agent': 'Android/22 MyGP/166 (en)'}
    headers_bal.update(get_hp('h',gpinfo))
    res = get('https://mygp.grameenphone.com/mygpapi/balance',headers=headers_bal,params=get_hp('p',gpinfo)).json()
    return res

def get_formated_data_bal():
    try:
        raw_bal = get_balance_raw()
        total = raw_bal['internet_details']
        msg = 'Total Balance: '+total['value'] + ' ' + total['unit']

        for p in raw_bal['internet_packs']:
            if(int(p['value'].split(' ')[0])==0):
                continue
            m = '\n\nPack: {}\n'.format(p['name']) + \
                'Remaining: {}\n'.format(p['value']) + \
                'Validity: {}'.format(p['remaining'])
            msg += m

        return msg
    except:
        print(format_exc())
        return 'Something went wrong.\n\n' + str(raw_bal)
