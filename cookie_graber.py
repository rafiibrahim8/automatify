# This file will be run on your local machine to extract cookies from Firefox

import json
import base64
import browser_cookie3

required_cookie = ['c_user', 'datr', 'fr', 'sb', 'xs']
cookies = browser_cookie3.Firefox(domain_name='facebook.com').load()
d = dict()

for c in cookies:
    if(c.name in required_cookie):
        d[c.name] =  c.value
        required_cookie.remove(c.name)

if(required_cookie):
    print('Can not find these required cookies:', required_cookie)
    exit(code=1)

cookie_b64 = base64.b64encode(json.dumps(d).encode()).decode()
print(cookie_b64)
try:
    with open('cookie.txt','w') as f:
        f.write(cookie_b64)
except:
    print('File saving failed.')
