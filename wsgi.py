from flask import Flask
from flask import request as f_req
from dbms import add_db
from helper import update_h, delete_h, info_h
from base64 import b64decode
from json import loads,dumps
from service_handler import manage_hook_post, sendMessage
from adata import do_corn

import os
import threading

FB_WEBHOOK_PATH = '/' + os.environ['FB_WEBHOOK_PATH']

app = Flask(__name__)
app.config['MONGODB_DB'] = 'automatify'
add_db(app)

@app.route("/")
def hello():
    return "I am doing something in the background!"

@app.route("/robots.txt")
def robots_txt():
    return "User-agent: *\nDisallow: /\n"

@app.route(FB_WEBHOOK_PATH, methods = ['GET'])
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
        return 'Invalid mode', 400

@app.route(FB_WEBHOOK_PATH, methods = ['POST'])
def fb_hook_post():
    json_data = f_req.get_json()
    #print('Received:',json_data)
    if(json_data.get('object', None) == 'page'):
        t = threading.Thread(target=manage_hook_post,args=(json_data.get('entry',{}),))
        t.start()
        return 'received'
    else:
        return '404 - Not Found', 404

@app.route('/update', methods = ['POST'])
def update():
    return update_h(f_req.get_json())

@app.route('/delete', methods = ['POST'])
def delete():
    return delete_h(f_req.get_json())

@app.route('/info', methods = ['POST'])
def info():
    return info_h(f_req.get_json())

@app.route('/cron', methods = ['GET'])
def cron_func():
    res = do_corn()
    if(res[0] == 1):
        sendMessage(res[1],'UPDATE')
    return res[1]

# run using: flask run
