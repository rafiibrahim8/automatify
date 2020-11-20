from flask import Flask
from flask import request as f_req
from utils import db
from automatify_service_handler import handle_service
from adata import do_corn

import os
import requests
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

def printIP():
    try:
        print('Server IP:',requests.get('https://ifconfig.me').text)
    except:
        print('Can not get server IP.')

def sendMessage(text, msg_type='RESPONSE'):
    json = {
        'messaging_type': msg_type,
        'recipient':{'id': os.environ['MY_PSID']},
        'message':{
            'text': text
            }
        }
    params =  { 'access_token': os.environ['FB_PAGE_ACCESS_TOKEN'] }

    try:
        res = requests.post('https://graph.facebook.com/v8.0/me/messages', params=params, json=json)
        print(res.text)
    except:
        pass

def manage_hook_post(data):
    for d in data:
        for i in d['messaging']:
            try:
                if (i['message'] and i['message']['text'] and i['sender']['id'] == os.environ['MY_PSID']):
                    res = handle_service(i['message']['text'])
                    if(res != None):
                        sendMessage(res)
            except:
                break

@app.route("/")
def hello():
    return "I am doing something in the background!"

@app.route('/fb-webhook', methods = ['GET'])
def fb_hook_verify():
    VERIFY_TOKEN = os.environ['FB_VERIFY_TOKEN']
    mode = f_req.args.get('hub.mode')
    token = f_req.args.get('hub.verify_token')
    challenge = f_req.args.get('hub.challenge')
    
    if (mode and token):
        # Checks the mode and token sent is correct
        if (mode == 'subscribe' and token == VERIFY_TOKEN):
            # Responds with the challenge token from the request
            print('WEBHOOK_VERIFIED')
            return challenge
        return '403 - Forbidden', 403
    else:
        return 'Invalid mode'

@app.route('/fb-webhook', methods = ['POST'])
def fb_hook_post():
    json_data = f_req.get_json()
    print('Received:',json_data)
    if(json_data.get('object', None) == 'page'):
        t = threading.Thread(target=manage_hook_post,args=(json_data.get('entry',{}),))
        t.start()
        return 'received'
    else:
        return '404 - Not Found', 404

@app.route('/corn', methods = ['GET'])
def corn_func():
    res = do_corn()
    if(res[0] == 1):
        sendMessage(res[1],'UPDATE')
    return res[1]

threading.Thread(target=printIP).start()

# run using: flask run

