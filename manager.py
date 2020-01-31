import subprocess
import queue
import threading
import copy
from client_thread import *
from protocol import *

global client

def serialize_parametrs(parameters):
    return "name=" + parameters[0] + " " + "dataset=" + parameters[1] + " " + "batch_size=" + parameters[2] + " " + "lr=" + parameters[3] + " " + "interval=" +parameters[4]

# def make_parameters(param_list):
#     parameters_new = []
#     parameters_new.append('--name=' + param_list[0])
#     parameters_new.append('--dataset=' + param_list[1])
#     parameters_new.append('--batch_size=' + param_list[2])
#     parameters_new.append('--lr=' + param_list[3])
#     parameters_new.append('--interval=' + param_list[4])
#     return parameters_new

# def subscriber(client):
#     while client.isAlive():
#         if client.q.empty():
#             continue
#         msg = client.q.get()
#         send(client.connection, msg)

class Manager(threading.Thread):
    def __init__(self, qOut, connection, kill_event):
        threading.Thread.__init__(self)
        self.qOut = qOut
        self.connection = connection
        global client
        self.client = client
        #self.client_parameters = -1 
        self.kill_event = kill_event
    def run(self):
        print('server is running...')
        while True:
            command = recv(self.connection)
            if command == -1:
                print("connection reset")
                self.kill_event.set()
                self.exec_command(['exit'])
                break
            if command is None:
                continue
            print('command ', command, 'is running...')
            if self.exec_command(command) == False:
                break
        print("manager stopped")

    def exec_command(self, command):
        
        if command[0] == 'set' and len(command) >= 2:
            self.client_parameters = command[1:]
            print("client params:", client.params)
            if self.client.params is not None:
                self.client.params = command[1:]
            else:
                client.params = command[1:]

        if command[0] == 'getParameters':
            try:
                self.qOut.put(bytes('parameters: {0}'.format(serialize_parametrs(client.params), end=''), encoding="UTF-8"))
            except:
                self.qOut.put(bytes('failed: {0}'.format('12'), encoding="UTF-8"))        
        
        if command[0] == 'start':
            #Обработка нажатия на клавишу "Старт": если не заданы параметры возвращаем ошибку
            if self.client.params is None:
                self.qOut.put(bytes('failed: {0}'.format('11'), encoding="UTF-8"))
                return True
            if self.client_parameters ==  -1:
                self.qOut.put(bytes('failed: {0}'.format('11'), encoding="UTF-8"))
                return True
            client.set_status(1)

        if command[0] == 'stop':
            if self.client.params is not None:
                client.status = 0
                self.client.stop_learning()
            return True

        if command[0] == 'exit':
            client.kill_event.set()
            self.kill_event.set()
            if self.client.params is not None:
                self.client.kill()
            return 
    
        if command[0] == 'check':
            print('command check')
            if self.client.params is not None:
                self.qOut.put(bytes('status: {0}'.format(str(self.client.status), end=''), encoding="UTF-8"))
            else:
                self.qOut.put(bytes('status: {0}'.format('0', end=''), encoding="UTF-8"))
            return True

        if command[0] == 'getLog':
            try:
                #self.client.set_output()
                client.q.queue.clear()
                client.set_output()
            except:
                pass
        return True
