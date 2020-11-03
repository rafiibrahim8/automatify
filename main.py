from flask import Flask
from flask import request as f_req
from automatify_service_handler import handle_service
import os
import requests
import threading

app = Flask(__name__)

def sendMessage(text, uid):
    json = {
        'recipient': { 'id': uid },
        'message': text,
        }
    params =  { 'access_token': os.environ['FB_PAGE_ACCESS_TOKEN'] }
    res = requests.post('https://graph.facebook.com/v8.0/me/messages', params=params, json=json)
    print(res.text)

def manage_hook_post(data):
    for d in data:
        for i in d['messaging']:
            if (i['message'] and i['message']['text']):
                res = handle_service(i['message']['text'])
                if(res != None):
                    sendMessage(res, i['sender']['id'])


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
    print('XXX', f_req.form)
    if(f_req.form.get('object', None) == 'page'):
        t = threading.Thread(target=manage_hook_post,args=(f_req.form.get('entry',{}),))
        t.start()
        return 'received'
    else:
        return '404 - Not Found', 404
    return 'ok'

  


if __name__ == "__main__":
    app.run()