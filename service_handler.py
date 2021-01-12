from adata import detail_text as adata_service
from gdata import detail_text as gdata_service
from dbms import map_fbid_to_user
import os
import requests
import logging

def get_service(name):
    name = name.lower()
    services = {
        'adata': adata_service,
        'gdata': gdata_service
    }
    return services.get(name)

def sendMessage(text, recipient, msg_type='RESPONSE'):
    json = {
        'messaging_type': msg_type,
        'recipient':{'id': recipient},
        'message':{
            'text': text
            }
        }
    params =  { 'access_token': os.environ['FB_PAGE_ACCESS_TOKEN'] }

    try:
        res = requests.post('https://graph.facebook.com/v8.0/me/messages', params=params, json=json)
        logging.log(logging.INFO, res.text)
    except:
        logging.log(logging.CRITICAL, 'Send Message Failed')

def manage_hook_post(data):
    for d in data:
        for i in d['messaging']:
            try:
                if (i['message'] and i['message']['text'] and i['sender']['id']):
                    msg = i['message']['text'].strip().lower()
                    service = get_service(msg.split(' ')[0])
                    user = map_fbid_to_user(i['sender']['id'])
                    if not user:
                        sendMessage('You are not subscribed. Please contact admin.', i['sender']['id'])
                        return
                    res, code = service(user)
                    if(code == 200):
                        sendMessage(res, i['sender']['id'])
                        return
            except:
                break

