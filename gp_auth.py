#Run on your local machine

import requests
from requests.exceptions import InvalidSchema
from hashlib import sha1
from random import random
from base64 import b64encode
import json
import re

PHONE_NO = '01XXXXXXXXXX'

def genID():
    s1s = sha1(str(random()).encode('utf-8')).hexdigest()
    return s1s[:8] + '-' + s1s[8:12] + '-' + s1s[12:16] + '-' + s1s[16:20] + '-' + s1s[20:32]

def get_gpinfo():
    headers = {
        'User-Agent': 'Android/22 MyGP/166 (en)',
        'Accept-Language': 'en',
        'Vary': 'Accept-Language',
        'Connection': 'close',
        'Accept-Encoding': 'gzip, deflate'
        }

    hash_ = requests.get('https://mygp.grameenphone.com/mygpapi/settings?hash=&lang=en',headers=headers).json()['hash']

    params = {
        'acr_values': 1,
        'scope':'openid profile email phone gp.mygpselfcare',
        'login_hint':'MCCMNC:47001',
        'prompt':'no_seam',
        'client_id':'gp-mygpselfcaregpid-android',
        'log_session_id': genID(),
        'ui_locales':'en',
        'telenordigital_sdk_version':'android_v2.3.3_5.1.1_web-view',
        'state': genID(),
        'response_type':'code',
        'redirect_uri':'gp-mygpselfcaregpid-android://gpid/oauth2callback'
        }

    session_headers = {
        'Connection': 'close',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; GT-S7582 Build/LMY49J) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en,en-US;q=0.8',
        'X-Requested-With': 'com.portonics.mygp'
        }

    session = requests.Session()
    session.headers = session_headers

    session.get('https://signin.gp-id.com/oauth/authorize', params=params) #get cookies

    data = {
        'phone': PHONE_NO,
        'stayLoggedI':True,
        'pt':18185, #no idea what is this
        'screenId':'signin-switchable',
        'action':'next',
    }
    session.post('https://signin.gp-id.com/id/signin-switchable',data=data) #will send sms

    data={
        'type':'client_info_event',
        'desc':'User submitted phone: "' + PHONE_NO + '"'
    }
    session.post('https://signin.gp-id.com/id/api/notification',data=data) #no idea what it does

    pin = input('PIN: ').strip()

    data = {
        'pin':int(pin),
        'stayLoggedIn':True,
        'pt':18126, #no idea what is this
        'screenId':'verify-phone',
        'action':'next'
    }

    code = None
    try:
        res = session.post('https://signin.gp-id.com/id/verify-phone',data=data)
    except InvalidSchema as ex:
        code = re.findall('code=([^&]+)',str(ex)).pop()

    json_ = {
        'code': code
    }
    params = {
        'lang':'en'
    }

    gpinfo = requests.post('https://mygp.grameenphone.com/mygpapi/v2/oauth/connectid/get-token/android',json=json_,headers=headers,params=params).json()

    # will get like:
    # {"access_token":"7b4d97ddddddddddb298f70e","refresh_token":"ddcdddddddddddd9e5c512d0ee","expire_at":1605766713,"is_primary":1,"id":"000000","email":""}

    me_ua = genID()

    headers_extra = {
        'FIRST': '1',
        'User-Agent': 'Android/22 MyGP/166 (en) ID/' + me_ua,
        'Authorization': 'Bearer '+ gpinfo['access_token'],
    }

    headers.update(headers_extra)
    params = {
        'hash':hash_,
        'lang':'en',
        'id': gpinfo['id']
    }

    msisdn = requests.get('https://mygp.grameenphone.com/mygpapi/me',headers=headers,params=params).json()['msisdn']

    gpinfo['hash'] = hash_
    gpinfo['msisdn'] = msisdn
    gpinfo['me_ua'] = me_ua

    with open('gpinfo.txt','w') as f:
        f.write(b64encode(json.dumps(gpinfo).encode('utf-8')).decode('utf-8'))

    print(gpinfo)

if __name__ == '__main__':
    get_gpinfo()
