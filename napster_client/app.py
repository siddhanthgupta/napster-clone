#!/usr/bin/python3
from flask import Flask, render_template, request
import json
import os
import random
import threading

from TCPServerClient import ThreadedTCPServer, ThreadedTCPRequestHandler, client
from communicator import Communicator
from file_sync import ThreadFileSync
from logic.data_handler import EmojiDAO
from logic.emoji_classifier import EmojiClassifier


app = Flask(__name__)


def get_temp_emoji_list(size):
    list_orig = []
    with open('logic/list.txt', 'r') as f:
        x = f.read().split('\n')
        for line in x:
            if(len(line) >= 4):
                list_orig.append(line[:-4])
    random.shuffle(list_orig)
    return list_orig[:size]


def get_emoji_list(emotion):
    dao = EmojiDAO()
    print("We received name as", emotion)
    list_out = []
    emoji_dicts = dao.retrieve_all_from_file()
    for key, value in emoji_dicts.items():
        if('classification' in value and value['classification'].lower() == emotion.lower()):
            list_out.append(key)
    classes = set()
    for key, value in emoji_dicts.items():
        if('classification' in value):
            classes.add(value['classification'])
#             if(value['classification'] == 'miscellaneous'):
#                 print(key,'is classified as miscellaneous')
#             print(value['classification'])
    print(classes)
    return list_out


def setUp(depth):
    list_orig = []
    classifier = EmojiClassifier(depth)
    with open('logic/list.txt', 'r') as f:
        x = f.read().split('\n')
        for line in x:
            if(len(line) >= 4):
                list_orig.append(line[:-4])
    all_emoji_data = classifier.compute_and_store(list_orig, depth)
#     print("Displaying Keys")
#     for key, value in all_emoji_data.items():
#         print(key)
    print('The number of new keys are ', len(all_emoji_data))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/downloadFile', methods=['POST'])
def downloadFile():
    print(request.get_json())
    response_data = {}
    filename = request.json['filename']
    # At this point, we call the database and query against emoji_name for
    # the response_data parameters
    # For now, we use random values

    c = Communicator()
    if(not c.get_user_list(filename)):
        response_data['error'] = 'No users found'

    return json.dumps(response_data)


@app.route('/itemList', methods=['POST'])
def itemList():
    response_data = {}
    c = Communicator()
    filelist = c.get_file_list()
    file_list_local = []
    for file in os.listdir(Communicator.doc_folder):
        if(os.path.isfile(os.path.join(Communicator.doc_folder, file)) and file[0] != '.'):
            file_list_local.append(file)
    file_list_final = list(set(filelist) - set(file_list_local))
    print("Sending list")
    response_data['list'] = file_list_final
    # print(response_data)
    return json.dumps(response_data)


@app.route('/selfItemList', methods=['POST'])
def already_on_local():
    response_data = {}
    file_list = []
    for file in os.listdir(Communicator.doc_folder):
        if(os.path.isfile(os.path.join(Communicator.doc_folder, file)) and file[0] != '.'):
            file_list.append(file)
    response_data['list'] = file_list
    return json.dumps(response_data)

if __name__ == '__main__':
    #     setUp(10)
        # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 9876

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)
    file_sync = ThreadFileSync()
    c = Communicator()
    c.register_user()
    app.run(debug=False, host='0.0.0.0')

    c.unregister_user()
    server.shutdown()
    server.server_close()
    file_sync.remove_watch()
    print('Server shutdown')
