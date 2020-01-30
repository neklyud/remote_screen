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
import importlib
from protocol import *


def subscriber(client):
    while client.isAlive():
        if client.q.empty():
            continue
        msg = client.q.get()
        print(msg)
        send(client.connection, msg)

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

def add_module(path):
    module_name = os.path.basename(path)
    package_name = os.path.dirname(path)
    module = importlib.import_module(module_name[:-3], package=package_name)
    return module

class server:
    def __init__(self, host='192.168.33.233', port=8686, domain=socket.AF_INET, sock_type=socket.SOCK_STREAM):
        self.socket = socket.socket(domain, sock_type)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.qOut = queue.Queue(maxsize=1)
    def handle(self):
        while True:
            print("waiting connection")
            connection, address = self.socket.accept()
            print("connection is set...")
            kill_event = threading.Event()
            sender = threading.Thread(target=sender_subscriber, args=(self.qOut, connection, kill_event), daemon=True)
            manag = manager.Manager(self.qOut, connection, kill_event)
            manag.start()
            sender.start()
            manag.join()
            sender.join()

serv = server()
serv.handle()
