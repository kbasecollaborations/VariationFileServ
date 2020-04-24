#!/usr/bin/python
#
# Flask server, woo!
#


"""The primary router for the Variation Caching Service API v1."""
import json
import flask
import uuid
import os






from flask import Flask, request, redirect, url_for, send_from_directory, Response
from src.Utils.VariationCache import VariationCache

from flask_cors import CORS





FILE_SERVER_LOCATION = '/kb/module/work'

# Setup Flask app.
app = Flask(__name__, static_folder=FILE_SERVER_LOCATION)
app.debug = True
CORS(app, supports_credentials=True)



@app.route('/', methods=['GET'])
def root():
    """Root route for the API which lists all paths."""
  #TODO: put some message here
    return None


@app.route('/create_cache', methods=['POST'])
def create_cache():
    """Fetch a file given a shock ID."""
    try:
        params = json.loads(flask.request.get_data())    
    except Exception:
        raise RuntimeError('Unable to parse JSON request body.')
    auth_token = flask.request.headers.get('Authorization')

    base_url = flask.request.url.rsplit("/", 1)[0]

    
  

    #auth_token ="JJPRPDD7XZWC54Q7WE2HKM3AWZDKZL3F" 
    url = "https://appdev.kbase.us/services/"
    #variation_ref = "39465/42/22"
    variation_ref = params['variation_ref']
    
    #Create cached files given a variation ref
    vc = VariationCache(url, auth_token, FILE_SERVER_LOCATION)
    resp = vc.create_cache_variation(variation_ref, base_url)


    '''
    return json with a dictionary of server urls for snp.vcf.gz,
    snp.vcf.gz.tbi, assembly.fa, assembly.fa.faidx, genome.gff.gz,
    genome.gff.gz.tbi

    TODO: Question: Can the service url be set from the config?
    TODO: Need to figure out how to get the service_url during run time
    {
        "snp.vcf.gz" : "service_url/data/uuid/shock_id/snp.vcf.gz",
        "snp.vcf.gz" : "service_url/data/uuid/shock_id/snp.vcf.gz.tbi",
        "aseembly.fa" : "service_url/data/uuid/shock_id/assembly.fa",
        "aseembly.fa.faidx" : "service_url/data/uuid/shock_id/assembly.fa.faidx",
        "genome.gff.gz" : "service_url/data/uuid/shock_id/genome.fa.gz",
        "genome.gff.gz.tbi" : "service_url/data/uuid/shock_id/genome.fa.gz.tbi",
        "metadata" : "service_url/metadata/uuid/shock_id/metadata"
    }
    '''
    #print (resp)
    js = json.dumps(resp)
    resp = Response(js, status=200, mimetype='application/json')
    return resp







    #resp = vu.create_cache(shock_id, source, FILE_SERVER_LOCATION, md5)

    #if resp is not None:
    #    return (flask.jsonify(resp))
    #else:
    #    raise RuntimeError ("Error in creating cache")



@app.route('/dataset/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type

    return app.send_static_file(path)






if __name__ == '__main__':
  app.run()

