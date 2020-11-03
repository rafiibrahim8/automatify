from flask import Flask
from flask import request as f_req
from automatify_service_handler import handle_service
import os
import json
import requests
import threading

app = Flask(__name__)

def sendMessage(text):
    json = {
        "messaging_type": "UPDATE",
        "recipient":{"id": os.environ['MY_PSID']},
        "message":{
            "text": text
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
                    sendMessage(handle_service(i['message']['text']))
            except:
                break


@app.route("/")
def hello():
    return "Hello World!"

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


if __name__ == "__main__":
    app.run()