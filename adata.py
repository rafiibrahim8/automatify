from requests import Session
import os

WARN_DATA_LOW = 512.0

session = None
data_warn = False

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
