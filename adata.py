from traceback import format_exc
import requests
from json import loads,dumps
from dbms import update,querys, Users
import os

WARN_DATA_LOW = 512.0
AIRTEL_LOGIN_DASHBOARD_URL = 'https://www.bd.airtel.com/en/auth/login?redirectTo=/en/dashboard'     #GET
AIRTEL_LOGIN_URL = 'https://api.bd.airtel.com/v1/account/login/facebook'                            #POST

def init_session(user):
    session = requests.Session()
    session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/82.0'}
    cookies = querys(Users, 'airtel_cookies',user)
    if(cookies):
        session.cookies = requests.utils.cookiejar_from_dict(cookies)
    return session

def refresh_token(session,user):
    try:
        airtel_json = {
            'provider_access_token': 'does_not_matter',
            'provider_id': querys(Users,'airtel_fb_graph_id',user),
            'name': None,
            'profile_picture': None,
            'email':None,
            'provider':'facebook'
        }
        cookies = session.cookies.get_dict()
        cookies.pop('airtel_website_session')
        session.cookies = requests.utils.cookiejar_from_dict(cookies)
        session.get(AIRTEL_LOGIN_DASHBOARD_URL) # refresh 'airtel_website_session'.
        
        airtel_website_session = session.cookies.get_dict()['airtel_website_session']
        airtel_headers = {
            'X-CSRF-TOKEN': airtel_website_session,
            'Authorization':'Bearer ' + airtel_website_session
        }

        res = session.post(AIRTEL_LOGIN_URL, headers=airtel_headers, json=airtel_json)
        token = res.json().get('data').get('token')
        return token
    except:
        print(res.text)

def get_raw_res(retry=True, user=None, session=None, airtel_auth_session=None):
    if(not session):
        session = init_session(user)
    if(not airtel_auth_session):
        airtel_auth_session = querys(Users,'airtel_auth_session',user)
    if(not airtel_auth_session):
        refresh_token(session,user)
    try:
        headers = {'Authorization': 'Bearer ' + str(airtel_auth_session)}
        res = session.get('https://api.bd.airtel.com/v1/account/dashboard/internet',headers=headers)
        to_return = res.json()['data']['internetInfo']
        update(Users,'airtel_cookies',session.cookies.get_dict(), user)
        update(Users,'airtel_auth_session',airtel_auth_session, user)
        session.close()
        return to_return
    except:
        if(retry):
            print('Raw Data: Fetch failed. Trying again...')
            airtel_auth_session = refresh_token(session,user)
            return get_raw_res(False, user,session, airtel_auth_session)
        else:
            print('Raw Data: Someting went wrong.')
            session.close()
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

def detail_text(user=None, res=None):
    if(res == None):
        res = get_raw_res(user=user)
    res = format_msg(res)
    if(res == None):
        return 'Someting went wrong. Maybe logged out.', 200 # go through messenger
    return res, 200

def do_corn(user):
    data_warn =  querys(Users,'has_adata_warn',user)
    info = get_raw_res(user=user)
    try:
        remaining = float(info['total'] - info['usage'])
    except:
        print('Logged out.')
        return (2, 'Logged out\r\n')
    if(remaining < float(os.environ.get('AIRTEL_WARN_DATA_LOW', WARN_DATA_LOW))):
        if(not data_warn):
            update(Users,'has_adata_warn',True)
            return (1, 'Your data pack is about to finish.\n\n' + detail_text(res = info))
        else:
            return (0, 'Corn Done :)\r\n')
    else:
        update(Users,'has_adata_warn',False)
        return (0, 'Corn Done :)\r\n')
