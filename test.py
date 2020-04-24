import requests
import os
import json

# The URL of the running server from within the docker container
url = 'http://127.0.0.1:5000/create_cache'
#service_token = os.environ['KBASE_SECURE_CONFIG_PARAM_service_token']
os.environ['KBASE_SECURE_CONFIG_PARAM_service_token'] = ''


#url = 'https://appdev.kbase.us/dynserv/d184e3d4c94c63510ba6f29f6c1721b570982398.VariationFileServ/create_cache'
#url = "https://appdev.kbase.us/dynserv/7c2630c969594a6bbb009b5eecaedc5eda275efc.VariationFileServ/create_cache"
#url= "https://appdev.kbase.us/dynserv/4bbeefb86b2f3f2e14584b830504785e984f0d8a.VariationFileServ/create_cache"
#url = "https://appdev.kbase.us/dynserv/f1b4482974ac4ea5a7187aef173d5cfd91a66907.VariationFileServ/create_cache"

service_token="JJPRPDD7XZWC54Q7WE2HKM3AWZDKZL3F"

def make_request(variation_ref):
    """Helper to make a JSON RPC request with the given workspace ref."""
    post_data = {
            'variation_ref': variation_ref,
            'auth_token': service_token
             }
    headers = {'Content-Type': 'application/json', 'Authorization': service_token}
    resp = requests.post(url, data=json.dumps(post_data), headers=headers)
    return (resp.text)



variation_ref = "39465/42/22"
resp = make_request (variation_ref)
print (resp)
