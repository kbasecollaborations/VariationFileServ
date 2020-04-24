import requests
import hashlib
import binascii
import uuid
import os
from pathlib import Path
import subprocess
import errno


def run_command(command):

        cmdProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in cmdProcess.stdout:
            print(line.decode("utf-8").rstrip())
            cmdProcess.wait()
            print('return code: ' + str(cmdProcess.returncode))
            if cmdProcess.returncode != 0:
                raise ValueError('Error running: ' + command + 
                                 str(cmdProcess.returncode) + '\n')



def md5_sum_local_file(fname):
    md5hash = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5hash.update(chunk)
    return md5hash.hexdigest()




def create_link (source_file, link_path):
    os.link(source_file, link_path)
 


def _find(name, path, md5):
    #TODO: put some check for cache name
    #TODO: Make sure md5 of local file matches server information
    if  not os.path.isdir(path):
       raise RuntimeError(f" Specified file server path does not exist:{path}")
       return
    else:
        for root, dirs, files in os.walk(path):
            if name in files:
                resp = os.path.join(root, name)

                if (md5_sum_local_file(resp) == md5):
                    return (resp)
    return

def _mkdir_p(path):
    """
    _mkdir_p: make directory for given path
    """
    if not path:
        raise RuntimeError(f"Specified path is not valid:{path}")
        return
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise




def is_gz_file(filepath):
    with open(filepath, 'rb') as test_f:
        return binascii.hexlify(test_f.read(2)) == b'1f8b'