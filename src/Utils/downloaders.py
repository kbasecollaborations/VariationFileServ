import requests


def download_shock_file(url, token, shock_id, dest_path):
    """
    Download a file from shock.
    Args:
        shock_id
        md5
        dest_path
    Returns dict when the file finishes downloading
    """
    #_validate_file_for_writing(dest_path) #TODO validate
    headers = {'Authorization': ('OAuth ' + token) if token else None}
    # First, fetch some metadata about the file from shock
    shock_url = url + '/shock-api'
    node_url = shock_url + '/node/' + shock_id 

    print ("########" + node_url + "############")
    response = requests.get(node_url, headers=headers, allow_redirects=True)
    if not response.ok:
        raise RuntimeError(f"Error from shock: {response.text}")
    metadata = response.json()
    # Make sure the shock file is present and valid
    if metadata['status'] == 401:
        raise RuntimeError(f"Unauthorized access to shock file with ID:{ shock_id}")
    if metadata['status'] == 404:
        raise RuntimeError(f"Missing shock file with ID:{shock_id}")
    # Fetch and stream the actual file to dest_path
    with requests.get(node_url + '?download_raw',
                      headers=headers, allow_redirects=True, stream=True) as resp:
        with open(dest_path, 'wb') as fwrite:
            for block in resp.iter_content(1024):
                fwrite.write(block)

    return (dest_path)
