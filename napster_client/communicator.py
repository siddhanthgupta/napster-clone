'''
Created on 16-Mar-2016

@author: siddhanthgupta
'''
import hashlib
import json
import os
import random
import requests
import shutil
import socket

from TCPServerClient import client
from TCPServerClient import orig_dir


def get_my_ip_address():
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
        [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    return ip


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class Communicator:

    url = 'http://localhost:8000'
    doc_folder = orig_dir
    file_server_port = 9876
    ip = get_my_ip_address()

    def add_mapping_for_file(self, filename):
        url_to_send = Communicator.url + '/users_file/' + filename
        data = {'ip_address': Communicator.ip,
                'port': Communicator.file_server_port}
        data['filehash'] = str(
            md5(os.path.join(Communicator.doc_folder, filename)))
        if('filehash' not in data):
            print('Unable to calculate filehash')
            return
        response = requests.post(url_to_send, data)
        if(response.status_code != 201):
            print(response.text)
        else:
            print('File added')

    def add_all_files(self):
        for file in os.listdir(Communicator.doc_folder):
            if(os.path.isfile(os.path.join(Communicator.doc_folder, file)) and file[0] != '.'):
                self.add_mapping_for_file(file)

    def register_user(self):
        data = {'ip_address': Communicator.ip,
                'port': Communicator.file_server_port}
        response = requests.post(Communicator.url + '/users/', data=data)
        if(response.status_code != 201):
            print(response.text)
        else:
            print('User registered')
            self.add_all_files()

    def unregister_user(self):
        data = {'ip_address': Communicator.ip,
                'port': Communicator.file_server_port}
        response = requests.delete(Communicator.url + '/users/', data=data)
        if(response.status_code != 204):
            print(response.text)
        else:
            print('User unregistered')

    def get_file_list(self):
        response = requests.get(Communicator.url + '/files')
#         print(response.text)
        filelist = []
        resp_list = json.loads(response.text)
        for dict in resp_list:
            filelist.append(dict['filename'])
        print(filelist)
        return filelist

    def get_user_list(self, filename):
        url_to_send = Communicator.url + '/users_file/' + filename
        response = requests.get(url_to_send)
        if(response.status_code != 200):
            print('Unable to find users')
            print(response.text)
            return False
        else:
            print(response.text)
            user_list = json.loads(response.text)['users']
            md5_original = json.loads(response.text)['filehash']
            while(len(user_list) > 0):
                random_user_index = random.randint(0, len(user_list) - 1)
                random_user = user_list[random_user_index]
                user_list.pop(random_user_index)
                print(random_user)
                if(client(random_user['ip_address'], random_user['port'], filename, '/tmp')):
                    md5_downloaded = md5(os.path.join('/tmp', filename))
                    if(md5_downloaded == md5_original):
                        shutil.move(
                            os.path.join('/tmp', filename), os.path.join(Communicator.doc_folder, filename))
                        print('File transfer successful')
                        return True
                    else:
                        print('Invalid hash. Download scrapped')
            return False


# get_file_list()
# # get_my_ip_address()
# unregister_user()
# register_user()
# # add_all_files()
# get_user_list('ttf.txt')
# print(ip)
