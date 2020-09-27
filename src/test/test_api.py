"""
Simple integration tests on the API itself.

We make actual ajax requests to the running docker container.
"""
import os
import unittest

import requests
from dotenv import load_dotenv

from src.Utils.WorkspaceClient import Workspace

load_dotenv('.env')

print("###########################################\n")
print("See instructions for testing in Readme.md\n")
print("Tests fetch fasta shock node from assembly\n")
print("object and test if right bytes are retrieved\n")
print("###########################################\n")

token = os.environ['token']
if token is None:
    raise RuntimeError("Copy .env.example to .env in root "
                       "directory and fill token value token=XXXXXX ")

KBASE_ENDPOINT = os.environ['KBASE_ENDPOINT']
if KBASE_ENDPOINT is None:
    raise RuntimeError(
        "Copy .env.example to .env in root directory and "
        "fill KBASE_ENDPOINT=https://ci.kbase.us/services or as appropriate ")

print("kbase end point is :" + KBASE_ENDPOINT + "\n")
# The URL of the running server from within the docker container

base_url = 'http://web:5000'
cookie_info_good = "kbase_session=" + token
cookie_info_bad = "abc=def"
cookie_wrong_token = "kbase_session=" + "wrong_token"
cookie_empty_token = "kbase_session=" + ""



def get_assembly_shock_node():
    '''
    Get shock id from assembly ref
    '''
    # Get right workspace object for the environment
    # These shoule always be public narratives
    if KBASE_ENDPOINT.startswith("https://appdev.kbase.us/services"):
        assembly_ref = "47506/23/1"
        shock_api_url = "appdev.kbase.us/services/shock-api/node"
    elif KBASE_ENDPOINT.startswith("https://ci.kbase.us/services"):
        assembly_ref = "51623/7/2"
        shock_api_url = "ci.kbase.us/services/shock-api/node"
    else:
        raise RuntimeError("Supported environments: appdev or ci")

    ws_url = KBASE_ENDPOINT + "/ws"
    ws = Workspace(url=ws_url, token=token)
    try:
        fasta_shock_info = \
            ws.get_objects2({'objects':
                            [{"ref": assembly_ref,
                            'included': ['/fasta_handle_info/handle/id']}]})['data'][0]['data']
        fasta_shock_id = fasta_shock_info['fasta_handle_info']['handle']['id']
    except RuntimeError:
        print("Could not access shock object or shock node in" + assembly_ref)

    return (shock_api_url + "/" + fasta_shock_id)


def make_request(url, headers):
    """Helper to make a JSON RPC request with the given workspace ref."""
    print(url)
    print ("##################header###################")
    print(headers)
    resp = requests.post(url, headers=headers)
    return resp.text


class TestApi(unittest.TestCase):
    def test_0_no_cookie_header(self):
        '''
        Test no cookie in header
        '''

        print("\n\nrunning test: no cookie in header.")
        shock_node_url = get_assembly_shock_node()
        url = base_url + "/jbrowse_query/" + shock_node_url
        headers = {'Range': 'bytes:200-220'}
        resp = make_request(url, headers)
        self.assertTrue(resp.startswith("Error: Missing cookie in header"))
    # @unittest.skip('x')

    def test_1_download_selected_bytes(self):
        '''
        Get specified bytes from assembly node
        specify environment and token in .env file
        '''

        print("\n\nrunning test: Get specified bytes from assembly node for ci or appdev ")
        shock_node_url = get_assembly_shock_node()
        url = base_url + "/jbrowse_query/" + shock_node_url
        headers = {'Cookie': cookie_info_good, 'Range': 'bytes:200-220'}
        resp = make_request(url, headers)
        self.assertTrue(resp.startswith("TCAAAATGCTATGCTTTGTTC"))

    def test_2_bad_Cookie(self):
        '''
        Test for missing kbase_session in Cookie
        '''

        print("\n\nrunning test: Missing kbase session in cookie ")
        shock_node_url = get_assembly_shock_node()
        url = base_url + "/jbrowse_query/" + shock_node_url
        headers = {'Cookie': cookie_info_bad, 'Range': 'bytes:200-220'}
        resp = make_request(url, headers)
        self.assertTrue(resp.startswith("Error: Missing kbase_session in Cookie"))

    def test_3_empty_token(self):
        '''
        Test for missing kbase_session in Cookie
        '''

        print("\n\nrunning test: Empty token in cookie ")
        shock_node_url = get_assembly_shock_node()
        url = base_url + "/jbrowse_query/" + shock_node_url
        headers = {'Cookie': cookie_empty_token, 'Range': 'bytes:200-220'}
        resp = make_request(url, headers)
        self.assertTrue(resp.startswith("Error: empty token"))

    def test_4_unauthorized_token(self):
        '''
        Test unauthorized token
        '''

        print("\n\nrunning test: Unauthorized token ")
        shock_node_url = get_assembly_shock_node()
        url = base_url + "/jbrowse_query/" + shock_node_url
        headers = {'Cookie': cookie_wrong_token, 'Range': 'bytes:200-220'}
        resp = make_request(url, headers)
        self.assertTrue(resp.startswith("Error: Unauthorized token"))

    def test_5_out_of_range_bytes(self):
        '''
        Test out of range bytes.
        '''
        # TODO: improve this test. resp could be empty because of other reasons

        print("\n\nrunning test: out of range bytes")
        shock_node_url = get_assembly_shock_node()
        url = base_url + "/jbrowse_query/" + shock_node_url
        headers = {'Cookie': cookie_info_good, 'Range': 'bytes:1111111200-1111111202'}
        resp = make_request(url, headers)
        self.assertTrue(resp is '')

    # TODO: To make this test work in other environments
    #  upload src/test/my_test_genome_assembly.fa
    #  to other environments and update "get_assembly_shock_node"
    #  function

    # TODO: Update tests to include if the shock service itself is down
