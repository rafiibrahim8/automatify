# This file will be run on your local machine to extract cookies from Firefox

import json
import base64
import browser_cookie3

required_cookie = ['c_user', 'datr', 'fr', 'sb', 'xs']
cookies = browser_cookie3.Firefox(domain_name='facebook.com').load()
d = dict()

for c in required_cookie:
    d[c] =  cookies[c]

cookie_b64 = base64.b64encode(json.dumps(d).encode()).decode()
print(cookie_b64)
try:
    with open('cookie.txt','r') as f:
        f.write(cookie_b64)
except:
    print('File saving failed.')
