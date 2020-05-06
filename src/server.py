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
    print ("################################################################")
    server_base = 'https://appdev.kbase.us/services/shock-api/node/' + shock_id
    headers = Headers()
    status = None

    # Get total size of shock node
    resp = requests.get(server_base)
    rb = resp.json()
    size = rb['data']['file']['size']
    print (server_base)
    print (size)
    print (request.headers)
    # Handle byte range request properly
    if request.headers.has_key("Range"):
        status = 206
        ranges = findall(r"\d+", request.headers["Range"])
        begin = int(ranges[0])
        if len(ranges) > 1:
            end = int(ranges[1])

            # Request from shock with required bytes for input shock node
            server = server_base + '?download&seek=' + str(begin) + '&length=' + str(end - begin + 1)
            r = requests.get(server, stream=True)
            print (r.headers)

            # TODO: Send streamed content
            # TODO: Handle cases where this byte request goes above a certain limit
            # TODO: Figuring this requires some  digging of Jbrowse code
            data = r.content
            print (r.apparent_encoding)
            #data=BytesIO(r.content)
            print ("---------")
            print (sys.getsizeof(data))
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
        server = server_base + "?download_raw"
        # Make request
        r = requests.get(server, stream=True)
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
