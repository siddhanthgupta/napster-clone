'''
Created on 17-Mar-2016

@author: siddhanthgupta
'''

import os
import socket
import socketserver
import threading
import traceback


orig_dir = '/home/siddhanthgupta/apt-get log'


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        filename = str(self.request.recv(1024), 'ascii')
        file = open(os.path.join(orig_dir, filename), 'rb')
        filesize = os.stat(os.path.join(orig_dir, filename)).st_size
        print('filesize is', filesize)
#         self.request.sendall(bytes(str(filesize), 'ascii'))
        chunk = file.read(1024)
        while(chunk):
            self.request.sendall(chunk)
            chunk = file.read(1024)
        file.close()
        cur_thread = threading.current_thread()
        print('Server running in thread', cur_thread.name)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def client(ip, port, filename, dest_folder):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
    except Exception:
        sock.close()
        print('Exception occurred in getting file1')
        return False
    retr_flag = True
    try:
        sock.sendall(bytes(filename, 'ascii'))
#         filesize = int(str(sock.recv(1024), 'ascii'))
        file = open(os.path.join(dest_folder, filename), 'wb')
        chunk = sock.recv(1024)
        counter = 0
        while(chunk):
            file.write(chunk)
            counter += 1024
            percent = (counter / filesize) * 100.00
            if(percent > 100):
                percent = 100
            print('Received', percent, '%')
            chunk = sock.recv(1024)
    except Exception:
        print('Exception occurred in getting file2')
        retr_flag = False
        traceback.print_exc()
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    return retr_flag

# if __name__ == "__main__":
#     # Port 0 means to select an arbitrary unused port
#     HOST, PORT = "0.0.0.0", 0
#
#     server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
#     ip, port = server.server_address
#
#     # Start a thread with the server -- that thread will then start one
#     # more thread for each request
#     server_thread = threading.Thread(target=server.serve_forever)
#     # Exit the server thread when the main thread terminates
#     server_thread.daemon = True
#     server_thread.start()
#     print("Server loop running in thread:", server_thread.name)
#
#     client(ip, port, 'supergirl.jpg', '/tmp')
#
#     server.shutdown()
#     server.server_close()
#     print('Server shutdown')
