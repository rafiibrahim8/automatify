from requests import Session
from hashlib import sha1
from base64 import b64decode
from json import loads
from time import time
from re import findall
import os

WARN_DATA_LOW = 512.0
AIRTEL_PUBLIC_FACEBOOK_APP_ID = 688591131546006
OAUTH_URL = 'https://web.facebook.com/v2.3/dialog/oauth'                                            #GET
GRAPH_URL = 'https://graph.facebook.com/v2.3/me'                                                    #GET
AIRTEL_LOGIN_DASHBOARD_URL = 'https://www.bd.airtel.com/en/auth/login?redirectTo=/en/dashboard'     #GET
AIRTEL_LOGIN_URL = 'https://api.bd.airtel.com/v1/account/login/facebook'                            #POST

session = None
data_warn = False
airtel_auth_session = None

def init_session():
    global session
    if(session == None):
        session = Session()
        fb_cookies = loads(b64decode(os.environ['FB_COOKIES_B64'].encode()))
        for c in fb_cookies:
            session.cookies.set(c, fb_cookies[c])
        session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/82.0'}

def genarate_token():
    try:
        init_session()
        oauth_params = {
            'app_id': AIRTEL_PUBLIC_FACEBOOK_APP_ID,
            'auth_type': None,
            'cbt': int(time() * 1000),
            'channel_url': 'https://staticxx.facebook.com/x/connect/xd_arbiter/?version=46#cb=f1dd5e86ec40b7&domain=www.bd.airtel.com&origin=https%3A%2F%2Fwww.bd.airtel.com%2Ff11dcc402fa7cb8&relation=opener',
            'client_id': AIRTEL_PUBLIC_FACEBOOK_APP_ID,
            'display':'popup',
            'domain':'www.bd.airtel.com',
            'e2e': '{}',
            'fallback_redirect_uri': AIRTEL_LOGIN_DASHBOARD_URL,
            'locale':'en_US',
            'logger_id': sha1(str(time()).encode()).hexdigest()[:15],
            'origin': 1,
            'redirect_uri': 'https://staticxx.facebook.com/x/connect/xd_arbiter/?version=46#cb=f14672d502b76f8&domain=www.bd.airtel.com&origin=https%3A%2F%2Fwww.bd.airtel.com%2Ff11dcc402fa7cb8&relation=opener&frame=f4acbf7735c228',
            'response_type':'token,signed_request,graph_domain',
            'return_scopes': False,
            'scope':'public_profile,email',
            'sdk':'joey',
            'version':'v2.3',
            '_rdc':1,
            '_rdr': None
        }
        
        oauth_response = session.get(OAUTH_URL, params=oauth_params).text
        access_token= findall('access_token=([^&]+)', oauth_response).pop()

        graph_params = {
            'access_token': access_token,
            'fields':'name,email,picture',
            'locale':'en_US',
            'method':'get',
            'pretty': 0,
            'sdk':'joey',
            'suppress_http_code': 1
        }

        graph_response = session.get(GRAPH_URL, params=graph_params).json()

        airtel_json = {
            'provider_access_token': access_token,
            'provider_id': graph_response.get('id'),
            'name': graph_response.get('name'),
            'profile_picture': graph_response.get('picture').get('data').get('url'),
            'email':graph_response.get('email'),
            'provider':'facebook'
        }

        airtel_website_session =  session.get(AIRTEL_LOGIN_DASHBOARD_URL).cookies['airtel_website_session']

        airtel_headers = {
            'X-CSRF-TOKEN': airtel_website_session,
            'Authorization':'Bearer ' + airtel_website_session
        }

        token = session.post(AIRTEL_LOGIN_URL, headers=airtel_headers, json=airtel_json).json().get('data').get('token')
        return token
    except:
        return

def get_raw_res(retry=True):
    global airtel_auth_session
    try:
        init_session()
        headers = {'Authorization': 'Bearer ' + airtel_auth_session}
        res = session.get('https://api.bd.airtel.com/v1/account/dashboard/internet',headers=headers)
        return res.json()['data']['internetInfo']
    except:
        if(retry):
            print('Raw Data: Fetch failed. Trying again...')
            airtel_auth_session = genarate_token()
            return get_raw_res(False)
        else:
            print('Raw Data: Someting went wrong.')
            return

def format_msg(info):
    try:
        remaining = info['total'] - info['usage']
    except:
        return None
    percent = remaining*100/info['total']

    msg = 'Overall: {} MB\n'.format(info['total']) + \
        'Used: {} MB\n'.format(info['usage']) + \
        'Remaining: {:.2f} MB ({:.2f}%)\n\n'.format(remaining,percent)

    for p in info['packs']:
        remaining = p['total'] - p['usage']
        if(int(remaining) == 0):
            continue
        percent = remaining*100/p['total']
        validity = p['validity'].split('T')[0] + ' ' + p['validity'].split('T')[1][:5]

        m = 'Pack: {}\n'.format(p['title']) + \
            'Total: {} MB\n'.format(p['total']) + \
            'Used: {} MB\n'.format(p['usage']) + \
            'Remaining: {:.2f} MB ({:.2f}%)\n'.format(remaining,percent) + \
            'Validity: {}\n\n'.format(validity)
        msg += m
    
    return msg.strip()

def get_detail_text(res=None):
    if(res == None):
        res = get_raw_res()
    res = format_msg(res)
    if(res == None):
        return 'Someting went wrong. Maybe logged out.'
    return res

def do_corn():
    global data_warn
    info = get_raw_res()
    try:
        remaining = float(info['total'] - info['usage'])
    except:
        print('Logged out.')
        return (2, 'Logged out')
    if(remaining < float(os.environ.get('AIRTEL_WARN_DATA_LOW', WARN_DATA_LOW))):
        if(not data_warn):
            data_warn = True
            return (1, 'Your data pack is about to finish.\n\n' + get_detail_text(info))
    else:
        data_warn = False
        return (0, 'Corn Done :)')
