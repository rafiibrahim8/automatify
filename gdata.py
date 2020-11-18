from requests import get
from json import loads
from base64 import b64decode
import os

headers_common = None
params_common = None
gpinfo = None

def get_gpinfo():
    try:
        return loads(b64decode(os.environ['GP_INFO_B64'].encode()))
    except KeyError:
        try:
            with open('gpinfo.txt','rb') as f:
                return loads(b64decode(f.read()))
        except:
            return None

def init():
    global headers_common, params_common, gpinfo
    if(not gpinfo):
        gpinfo = get_gpinfo()
    if(not headers_common):
        headers_common = {
            'Accept-Language': 'en',
            'Vary': 'Accept-Language',
            'Authorization': 'Bearer '+ gpinfo['access_token'],
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate'
        }
    if(not params_common):
        params_common = {
            'hash': gpinfo['hash'],
            'lang':'en',
            'id': gpinfo['id']
        }

def get_my_details():
    init()
    headers_me = {
        'NOTFIRST': '1',
        'User-Agent': 'Android/22 MyGP/166 (en) ID/'+ gpinfo['me_ua'],
    }

    headers_me.update(headers_common)
    res = get('https://mygp.grameenphone.com/mygpapi/me',headers=headers_me,params=params_common).json()
    return res


def get_balance_raw():
    init()
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
        return 'Something went wrong.'

