import socket
import os
import subprocess
import threading
import queue

import manager
from protocol import *
from client_thread import *

global client    

def sender_subscriber(q, connection, e):
    while True:
        if e.is_set():
            break
        if q.empty():
            continue
        msg = q.get()
        print(msg)
        send(connection, msg)
    e.clear()

class server:
    def __init__(self, host='192.168.33.233', port=8686, domain=socket.AF_INET, sock_type=socket.SOCK_STREAM):
        self.socket = socket.socket(domain, sock_type)
        self.socket.bind((host, port))
        self.socket.listen(1)

        global client
        self.client = client # client_thread.client_thread(q=self.qOut)

    def handle(self):
        client.start() 
        while True:
            print("waiting connection")
            connection, address = self.socket.accept()
            print("connection is set...")
            kill_event = threading.Event()
            sender = threading.Thread(target=sender_subscriber, args=(client.q, connection, kill_event), daemon=True)
            manag = manager.Manager(client.q, connection, kill_event)
            manag.start()
            sender.start()
            manag.join()
            sender.join()

serv = server()
serv.handle()
