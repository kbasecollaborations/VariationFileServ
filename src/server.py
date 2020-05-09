#!/usr/bin/python
"""The primary router for the data service for API"""
import json
import os
import requests
from flask import Flask, request, redirect, url_for, send_from_directory, Response, stream_with_context, send_file
from flask_cors import CORS
from werkzeug.datastructures import Headers
from re import findall
from io import BytesIO
import sys
from urllib.parse import urlparse, urljoin
from http.cookies import SimpleCookie



# Set up server root path.
# TODO: COnfirm that the file server location matches with
# TODO: space that has enough space to host files
FILE_SERVER_LOCATION = '/kb/module/work'
#FILE_SERVER_LOCATION = '/Users/priyaranjan/kbasecode/VariationFileServ/test_local/workdir'
# Setup Flask app.
app = Flask(__name__, static_folder=FILE_SERVER_LOCATION)
app.debug = True
CORS(app, supports_credentials=True)


@app.route("/shock/<shock_id>")
def streamed_proxy(shock_id):
    """
    :param shock_id:
    :return:
    This method is used to support visualization of Variation data
    in Jbrowse. Jbrowse sends request to this method and this service
    returns required amount of bytes.
    :param shock_id:
    :return: bytes of data from shock id requested by Jbrowse
    #TODO: Support authenticated requests when supported by HTML report
    """

    # TODO: This should come from the jbrowse itself.
    # TODO: So instead of putting it as /shock/shock_id
    # TODO: put server/shock/shock_id the whole path of the node
    cookie_rawdata = request.headers["Cookie"]
    referring_url = request.headers["Referer"]

    #Get shock url with node id
    o = urlparse(referring_url)
    server_url = o.scheme + "://" + o.netloc
    node_url = server_url + "/services/shock-api/node/" + shock_id

    #Get token
    cookie = SimpleCookie()
    cookie.load(cookie_rawdata)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    token = cookies['kbase_session']

                          
    #Debugging statements
    #TODO: Remove anything that shows token
    print (request.headers)
    print (referring_url)
    print (cookie_rawdata)
    print (server_url)
    print (node_url)
    print (token)

    # Get total size of shock node
    auth_headers = {'Authorization': ('OAuth ' + token) if token else None}
    resp = requests.get(node_url, headers=auth_headers, allow_redirects=True)
    rb = resp.json()
    size = rb['data']['file']['size']
    print (size)

    headers = Headers()
    status = None
    # Handle byte range request properly
    if request.headers.has_key("Range"):
        status = 206
        ranges = findall(r"\d+", request.headers["Range"])
        begin = int(ranges[0])
        if len(ranges) > 1:
            end = int(ranges[1])

            # Request from shock with required bytes for input shock node
            effective_node_url = node_url + '?download&seek=' + str(begin) + '&length=' + str(end - begin + 1)
            r = requests.get(effective_node_url, headers=auth_headers, stream=True)
            print (r.headers)
            # TODO: Send streamed content
            # TODO: Handle cases where this byte request goes above a certain limit
            # TODO: Figuring this requires some  digging of Jbrowse code
            data = r.content
            print (r.apparent_encoding)
            # Add headers
            if end >= size:
                end = size - 1
            content_length = end - begin + 1
            content_range = "bytes " + str(begin) + "-" + str(end) + "/" + str(size)
            headers.add('Content-Length', str(content_length))
            headers.add('Content-Range', str(content_range))
            headers.add('Accept-Ranges', 'bytes')
            headers.add('Connection', 'keep-alive')
            headers.add('Cache-Control', 'public, max-age=43200')
            print (headers)
            # Send response with headers
            response = Response(data, status=status, headers=headers)
            return response
    # Handle non-byte range request
    # Needed to support smaller fasta index
    else:
        # server is the shock node url for downloading the whole file
        effective_node_url = node_url + "?download_raw"
        # Make request
        r = requests.get(effective_node_url, headers=auth_headers, stream=True)
        # Add headers and status
        status = r.status_code
        headers.add('Content-Length', r.headers['Content-Length'])
        headers.add('Accept-Ranges', 'bytes')
        # Create streamed response
        response = Response(r.iter_content(chunk_size=1024), status=status, headers=headers)
        return response


@app.route('/dataset/<path:path>')
def static_proxy(path):
    """
    This is used to support Jbrowse sessions.
    Each jbrowse session is a new directory that serves
    static javascript files
    :param path: path to the file on the system
    :return: content of the file
    """
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


if __name__ == '__main__':
    app.run()
