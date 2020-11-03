from requests import Session
import os

session = None
data_warn = False
WARN_DATA_LOW = 200.0 #MB

def init_session():
    global session
    if(session == None):
        session = Session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/82.0',
            'Authorization': 'Bearer ' + os.environ['AIRTEL_AUTH_SESSION']
        }

def get_raw_res():
    try:
        init_session()
        res = session.get('https://api.bd.airtel.com/v1/account/dashboard/internet')
        return res.json()['data']['internetInfo']
    except:
        print('Someting went wrong.')

def format_msg(info):
    remaining = info['total'] - info['usage']
    percent = remaining*100/info['total']

    msg = 'Overall: {} MB\n'.format(info['total']) + \
        'Used: {} MB\n'.format(info['usage']) + \
        'Remaining: {} MB ({:.2f}%)\n\n'.format(remaining,percent)

    for p in info['packs']:
        remaining = p['total'] - p['usage']
        if(int(remaining) == 0):
            continue
        percent = remaining*100/p['total']
        validity = p['validity'].split('T')[0] + ' ' + p['validity'].split('T')[1][:5]

        m = 'Pack: {}\n'.format(p['title']) + \
            'Total: {} MB\n'.format(p['total']) + \
            'Used: {} MB\n'.format(p['usage']) + \
            'Remaining: {} MB ({:.2f}%)\n'.format(remaining,percent) + \
            'Validity: {}\n\n'.format(validity)
        msg += m
    
    return msg.strip()

def get_detail_text(res=None):
    if(res == None):
        res = get_raw_res()
    if(res == None):
        return 'Someting went wrong.'
    return format_msg(res)


def do_corn():
    global data_warn
    info = get_raw_res()
    remaining = info['total'] - info['usage']
    if(remaining < WARN_DATA_LOW):
        if(not data_warn):
            data_warn = True
            return 'Your data pack is about to finish.\n\n' + get_detail_text(info)
    else:
        data_warn = False
        return None
