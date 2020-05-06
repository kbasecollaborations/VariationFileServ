import requests
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder


def download_shock_file(url, token, shock_id, dest_path):
    """
    Download a file from shock.
    Args:
        shock_id
        dest_path
    Returns dict when the file finishes downloading
    """
    # _validate_file_for_writing(dest_path) #TODO validate
    headers = {'Authorization': ('OAuth ' + token) if token else None}
    # First, fetch some metadata about the file from shock
    shock_url = url + '/shock-api'
    node_url = shock_url + '/node/' + shock_id

    print("########" + node_url + "############")
    response = requests.get(node_url, headers=headers, allow_redirects=True)
    if not response.ok:
        raise RuntimeError(f"Error from shock: {response.text}")
    metadata = response.json()
    # Make sure the shock file is present and valid
    if metadata['status'] == 401:
        raise RuntimeError(f"Unauthorized access to shock file with ID:{shock_id}")
    if metadata['status'] == 404:
        raise RuntimeError(f"Missing shock file with ID:{shock_id}")
    # Fetch and stream the actual file to dest_path
    with requests.get(node_url + '?download_raw',
                      headers=headers, allow_redirects=True, stream=True) as resp:
        with open(dest_path, 'wb') as fwrite:
            for block in resp.iter_content(1024):
                fwrite.write(block)

    return (dest_path)


def unpack_jbrowse_files(shock_file_path, dest_directory):
    """
    This method is used to created jbrowse session by extracting
    javascript files and all related data from a zip file
    :param shock_file_path:
    :param dest_directory:
    :return:
    """
    file_dir = os.path.dirname(file_path)
    with zipfile.ZipFile(file_path) as zf:
        zf.extractall(file_dir)
    index_path = os.path.join(file_dir, "jbrowse", "index.html")
    if (os.path.exists(index_path)):
        raise RuntimeError("index_path " + index_path + " was not created")
    else
        return index_path


def public_read_acl_shock(url, token, shock_id):
    """
    Make shock node public
    """
    # _validate_file_for_writing(dest_path) #TODO validate

    headers = {'Authorization': ('OAuth ' + token) if token else None}
    # First, fetch some metadata about the file from shock
    shock_url = url + '/shock-api'
    node_url = shock_url + '/node/' + shock_id + "/acl/public_read"

    print("########" + node_url + "############")

    response = requests.put(node_url, headers=headers)
    resp = json.loads(response.text)
    status = resp.get('status')
    return (status)


def upload_shock_file_public_read(url, token, file_path):
    """
    Uploads file to shock
    Taken from DFU code
    File is uploaded in public-read
    :param url:
    :param token:
    :param file_path:
    :return: shock_id
    """
    shock_url = url + "/shock-api"
    with open(os.path.abspath(file_path), 'rb') as data_file:
        files = {'upload': (os.path.basename(file_path), data_file, None,
                            {'Content-Length': os.path.getsize(file_path)})}
        mpe = MultipartEncoder(fields=files)
        headers['content-type'] = mpe.content_type
        response = requests.post(
            shock_url + '/node', headers=headers, data=mpe,
            stream=True, allow_redirects=True)
    shock_data = response.json()['data']
    shock_id = shock_data['id']
    if shock_id is not None:
        public_read_status = public_read_acl_shock(url, token, shock_id)
        if public_read_status is not None:
            return shock_id
        else:
            raise RuntimeError("could not change acl of shock id " + shock_id)
    else:
        raise RuntimeError("File was not uploaded to shock properly")



def compress_jbrowse_folder(url, token, dest_dir):
    shock_url = url + "/shock-api"
    if not token:
        raise ValueError('Authentication token required.')
    headers = {'Authorization': 'Oauth ' + token}
    file_path = params.get('file_path')
    if not file_path:
        raise ValueError('No file(s) provided for upload to Shock.')
    pack = params.get('pack')
    if pack:
        file_path = self._pack(file_path, pack)
    print ('uploading file ' + str(file_path) + ' into shock node')
    with open(os.path.abspath(file_path), 'rb') as data_file:
        # Content-Length header is required for transition to
        # https://github.com/kbase/blobstore
        files = {'upload': (os.path.basename(file_path), data_file, None,
                            {'Content-Length': os.path.getsize(file_path)})}
        mpe = MultipartEncoder(fields=files)
        headers['content-type'] = mpe.content_type
        response = requests.post(
            shock_url  + '/node', headers=headers, data=mpe,
            stream=True, allow_redirects=True)
    shock_data = response.json()['data']
    shock_id = shock_data['id']
    self.log('uploading done into shock node: ' + shock_id)
    if shock_id is not None:
        public_read_status = public_read_acl_shock(url, token, shock_id)
        if public_read_status is not None:
            return shock_id
        else:
            raise RuntimeError("could not change acl of shock id " + shock_id)
    else:
        raise RuntimeError("File was not uploaded to shock properly")
