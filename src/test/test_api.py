"""
Simple integration tests on the API itself.

We make actual ajax requests to the running docker container.
"""
import os
import json
import unittest
import requests
from dotenv import load_dotenv

load_dotenv('.env')


# The URL of the running server from within the docker container
url = 'http://127.0.0.1:5000'
service_token = os.environ['KBASE_SECURE_CONFIG_PARAM_service_token']
os.environ['KBASE_SECURE_CONFIG_PARAM_service_token'] = ''


def make_request(ws_ref):
    """Helper to make a JSON RPC request with the given workspace ref."""
    post_data = {
        'params': {
            'ws_ref': ws_ref,
            'n_max_results': 2,
            'bypass_caching': True
        },
        'method': 'get_homologs',
        'id': 0
    }
    headers = {'Content-Type': 'application/json', 'Authorization': service_token}
    resp = requests.post(url, data=json.dumps(post_data), headers=headers)
    return resp.json()


class TestApi(unittest.TestCase):

    # @unittest.skip('x')
    def test_search_reads_paired(self):
        """Test a search on genome read data with paired-ends."""
        reads_ref = '15/45/1'
        json_resp = make_request(reads_ref)
        result = json_resp['result']
        print (result)
        #self.assertTrue(len(result['distances']))

