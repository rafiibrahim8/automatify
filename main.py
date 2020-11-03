from flask import Flask
from flask import request as f_req
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/fb-webhook', methods = ['GET'])
def fb_hook():
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
  


if __name__ == "__main__":
    app.run()