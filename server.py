import socket
import manager
import parser
import codecs
import os
import subprocess
import sys
import threading
import client_thread
import queue
from protocol import *

def subscriber(client):
    while client.isAlive():
        if client.q.empty():
            continue
        msg = client.q.get()
        print(msg)
        send(client.connection, msg)


class server:
    def __init__(self, host='192.168.33.233', port=8686, domain=socket.AF_INET, sock_type=socket.SOCK_STREAM):
        self.socket = socket.socket(domain, sock_type)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.manager = manager.Manager()
        self.parser = parser.Parser()
    def handle(self):
        while True:
            connection, address = self.socket.accept()
            start_command = recv(connection)
            q = queue.Queue(maxsize=1)
            client = client_thread.client_thread(connection, start_command[1], q)
            print("new connection from {address}".format(address=address))
            while True:
                command = recv(connection) 
                print(command)
                if command is None:
                    continue
                sender = threading.Thread(target=subscriber, args=(client,))         
                if command == 'run':
                    print('process is started:', start_command[1])
                    client.start()
                    sender.start()
                elif command[0] == 'stop':
                    print('process is stopped')
                    sender.killed = True
                    client.kill()
                elif command[0] == 'exit':
                    print("Connection is closed")
                    connection.close()
                    break
                
                        
serv = server()
serv.handle()