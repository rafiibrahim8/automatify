# This file will be run on your local machine to extract cookies from Firefox

import json
import base64
import browser_cookie3

d = dict()

for c in browser_cookie3.Firefox(domain_name='facebook.com').load():
    d[c.name] =  c.value

print(base64.b64encode(json.dumps(d).encode()).decode())

