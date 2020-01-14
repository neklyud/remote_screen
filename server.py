import socket
import manager
import parser
import codecs
import os
import subprocess
import sys
import threading

def output_reader(proc, connection):
    for line in iter(proc.stdout.readline, b''):
        try:
            print(148888888)
            connection.send(bytes('got line: {0}'.format(line.decode('utf-8'), end=''), encoding="UTF-8"))
        except IOError:
            return
        print('got line: {0}'.format(line.decode('utf-8')), end='')
        proc.stdout.flush()

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
            print("new connection from {address}".format(address=address))
            command_len = int(connection.recv(4).decode("UTF-8"))
            command = str(connection.recv(command_len).decode("UTF-8")).split()
            print(command_len)
            print(command)
            print(command[0]=='start', len(command[0]))
            if command[0] == 'start':
                print('process is started:', command[1])
                connection.send(bytes('get', encoding='UTF-8'))
                proc = subprocess.Popen(['python3', '-u', '-m', command[1]],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                print(1234)
                output_reader(proc, connection)
            elif command[0] == 'stop':
                print('process is stopped')
                os.kill(proc.pid, signal.SIGTERM)
            elif command[0] == 'exit':
                connection.close()
                print("Connection is closed")
                break
            elif command[0] == 'skip':
                continue       
            connection.send(b'stop')

serv = server()
serv.handle()