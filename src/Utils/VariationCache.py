import requests
import hashlib
import binascii
import uuid
import os
from pathlib import Path
import errno
import subprocess
from kbase_workspace_client import WorkspaceClient

from src.Utils.file_utils import  _mkdir_p,  run_command  

from src.Utils.downloaders import download_shock_file

import shutil

#TODO: remove _ from functions



class VariationCache:

    def __init__(self, url, token, file_server_root):
        '''
        standard path for caching shock files 
           root/data/shock/uuid/md5

        standaed path for md5
           root/data/md5/md5.log

        standard path for server files
           root/data/files/335_1_2.vcf.gz
           This file references the shock path
           if the link is broken user will have to create one

        workflow: 
        1. if shock id exists on the system - note its path
        2. link the session path to shock for serving

        '''
        self._url = url.strip('/')
        self._token = token

        self._root = file_server_root
        

        session_uuid = str(uuid.uuid4())

        self._datapath = os.path.join(file_server_root, "data")

        self._md5path = os.path.join(self._datapath, "md5path")
        self._session_path = os.path.join(self._datapath,  "session" ,session_uuid)

        self._jbrowse_session_path = os.path.join(self._session_path,  "jbrowse")


        self._save_dir = os.path.join(self._datapath , "shock",  session_uuid)


        



    def create_dirs (self):

        if not os.path.isdir(self._datapath):
            _mkdir_p (self._datapath)

        if not os.path.isdir(self._md5path):
            _mkdir_p (self._md5path)

        if not os.path.isdir(self._session_path):
            _mkdir_p (self._session_path)

        if not os.path.isdir(self._save_dir):
            _mkdir_p (self._save_dir)

         


    def create_session_dirs (self, shock_id):

        if shock_id is None:
            raise RuntimeError('invalid shock_id:' + shock_id)

        if not os.path.isdir(self._save_dir):
            _mkdir_p (self._save_dir)
        
        if not os.path.isdir(self._serve_dir):
            _mkdir_p (self._serve_dir)
     


    def force_symlink(self,src, link):
        try:
            os.symlink(src, link)
        except OSError as e:
            if e.errno == errno.EEXIST:
                os.remove(link)
                os.symlink(src, link)

        print (src, link)
        return (link)


    def get_cached_md5 (self, md5):
        '''
        check if md5 has ever been downloaded and is not deleted
        '''

        #TODO fix md5path
        md5path = self._md5path
        linkPath = os.path.join(md5path, md5)
        realPath = os.path.realpath(linkPath)

        if os.path.exists(realPath):
            return (realPath)

        
    def create_md5_cache (self, md5, dest_path):

        if self.get_cached_md5(md5):
            return (self.get_cached_md5(md5))
        else:
            md5path = self._md5path
            linkPath = os.path.join(md5path, md5)
            print (linkPath)
            if self.force_symlink (dest_path, linkPath):
                return(self.get_cached_md5(md5))


    def create_cache (self, shock_handle):

        shock_id = shock_handle['id']
        md5 = shock_handle['remote_md5']
        #link_path = self._serve_dir + "/" + shock_handle['file_name']

        resp = None

        cache_location = self.get_cached_md5 (md5)
        if cache_location is not None:
            return (cache_location)
        else:
            #TODO: make sure there are no trailing / in file_server
            
            dest_path = self._save_dir  + "/" + shock_id
            path_info = download_shock_file(self._url, self._token,  shock_id, dest_path)
            if path_info:
                cache_location = self.create_md5_cache (md5, path_info)
                return (cache_location)

    def create_server_access_path(self, src,  filename, base_url):
        '''

        '''
        #TODO fix session path
        path = self._jbrowse_session_path + "/data" 
        linkpath = os.path.join(path, filename) 
        server_access_path = self.force_symlink(src, linkpath)

        #print (src, linkpath)
        server_access_url = "dataset" + server_access_path.replace(self._root, "") 
        return (server_access_url)




    def create_assembly_index(self, assembly_path):
        assembly_index_path = assembly_path + ".fai"
        if not os.path.exists(assembly_index_path):
           cmd =  "samtools faidx " + assembly_path
           run_command(cmd)
        print (assembly_index_path)
        return (assembly_index_path)


            

    def create_cache_variation (self, variation_ref, base_url):

        self.create_dirs()

        self._jbrowse_static = os.path.join("/kb/module/deps/jbrowse")

       
        
        destination = shutil.copytree(self._jbrowse_static, self._jbrowse_session_path, copy_function = shutil.copy) 

        print (destination)
        print (os.listdir(destination))


        ws_url = self._url + "/" + "ws"

        ws = WorkspaceClient(url=ws_url, token=self._token)
        resp = None
        variation_obj = ws.req("get_objects2", {'objects': [{"ref": variation_ref}]})['data'][0]['data']
        #TODO: Fix the assembly ref typo
        assembly_ref = variation_obj['assemby_ref']
        assembly_obj = ws.req("get_objects2", {'objects': [{"ref": assembly_ref}]})['data'][0]['data']

        variation_shock_handle = variation_obj['vcf_handle']
        variation_index_shock_handle = variation_obj['vcf_index_handle']
        assembly_shock_handle = assembly_obj["fasta_handle_info"]["handle"]





        
        vcf_path = self.create_cache (variation_shock_handle)
        vcf_index_path = self.create_cache (variation_index_shock_handle)
        assembly_path = self.create_cache (assembly_shock_handle) 

        assembly_index_path = self.create_assembly_index(assembly_path)


        variation_ref_str = variation_ref.replace("/", "-")

        #TODO: Bring this back

        #vcf_name = variation_ref_str + "_" + "data.vcf.gz"
        #vcf_index_name = vcf_name + ".tbi"
        #assembly_name = variation_ref_str + "_" + "assembly.fa"
        #assembly_index_name = assembly_name + ".fai"



        



        vcf_name = "x.vcf.gz"
        vcf_index_name = vcf_name + ".tbi"
        assembly_name = "x.fa"
        assembly_index_name = assembly_name + ".fai"





        
        vcf_server_access_path = self.create_server_access_path (vcf_path, vcf_name, base_url )
        vcf_index_server_access_path = self.create_server_access_path (vcf_index_path,  vcf_index_name, base_url)
        assembly_server_access_path = self.create_server_access_path (assembly_path,  assembly_name, base_url)
        assembly_index_server_access_path = self.create_server_access_path (assembly_index_path, assembly_index_name, base_url)

        index_path = self._jbrowse_session_path.replace("/kb/module/work","")
        jbrowse_index = "dataset" + index_path + "/index.html"
 

        resp = {
           "vcf": vcf_server_access_path,
           "vcf_index": vcf_index_server_access_path,
           "assembly" : assembly_server_access_path,
           "assembly_index": assembly_index_server_access_path,
           "jbrowse": jbrowse_index
        }

        #print (resp)
        return (resp)





    #TODO: Write code to delete cache



