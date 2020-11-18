from traceback import format_exc
from requests import Session
import os

WARN_DATA_LOW = 512.0
AIRTEL_LOGIN_DASHBOARD_URL = 'https://www.bd.airtel.com/en/auth/login?redirectTo=/en/dashboard'     #GET
AIRTEL_LOGIN_URL = 'https://api.bd.airtel.com/v1/account/login/facebook'                            #POST

session = None
data_warn = False
airtel_auth_session = None

def init_session():
    global session
    if(session == None):
        session = Session()
        session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/82.0'}

def genarate_token():
    try:
        init_session()
        airtel_json = {
            'provider_access_token': 'does_not_matter',
            'provider_id': os.environ['AIRTEL_FB_GRAPH_ID'],
            'name': None,
            'profile_picture': None,
            'email':None,
            'provider':'facebook'
        }
        if(not session.cookies.get_dict().get('airtel_website_session')):
            session.get(AIRTEL_LOGIN_DASHBOARD_URL) # fetch 'airtel_website_session' cookies if not present.
        
        airtel_website_session = session.cookies.get_dict()['airtel_website_session']
        airtel_headers = {
            'X-CSRF-TOKEN': airtel_website_session,
            'Authorization':'Bearer ' + airtel_website_session
        }

        token = session.post(AIRTEL_LOGIN_URL, headers=airtel_headers, json=airtel_json).json().get('data').get('token')
        return token
    except:
        print(format_exc())

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
        return (2, 'Logged out\r\n')
    if(remaining < float(os.environ.get('AIRTEL_WARN_DATA_LOW', WARN_DATA_LOW))):
        if(not data_warn):
            data_warn = True
            return (1, 'Your data pack is about to finish.\n\n' + get_detail_text(info))
        else:
            return (0, 'Corn Done :)\r\n')
    else:
        data_warn = False
        return (0, 'Corn Done :)\r\n')
