import subprocess
import client_thread
import queue
import threading
from protocol import *

def serialize_parametrs(parameters):
    return "name=" + parameters[0] + " " + "dataset=" + parameters[1] + " " + "batch_size=" + parameters[2] + " " + "lr=" + parameters[3] + " " + "interval=" +parameters[4]

def make_parameters(param_list):
    parameters_new = []
    parameters_new.append('--name=' + param_list[0])
    parameters_new.append('--dataset=' + param_list[1])
    parameters_new.append('--batch_size=' + param_list[2])
    parameters_new.append('--lr=' + param_list[3])
    parameters_new.append('--interval=' + param_list[4])
    return parameters_new

def subscriber(client):
    while client.isAlive():
        if client.q.empty():
            continue
        msg = client.q.get()
        send(client.connection, msg)

class Manager(threading.Thread):
    def __init__(self, qOut, connection, kill_event):
        threading.Thread.__init__(self)
        self.qOut = qOut
        self.connection = connection
        self.client = None
        self.client_parameters = -1 
        self.kill_event = kill_event
    def run(self):
        print('server is running...')
        while True:
            command = recv(self.connection)
            if command == -1:
                print("connection reset")
                self.kill_event.set()
                if self.client is not None:
                    self.client.kill()
                self.connection.close()
                break
            if command is None:
                continue
            print('command ', command, 'is running...')
            if self.exec_command(command) == False:
                break
        print("task done")

    def exec_command(self, command):
        
        if command[0] == 'set' and len(command) >= 2:
            self.client_parameters = command[1:]

        if command[0] == 'getParameters':
            try:
                self.qOut.put(bytes('parameters: {0}'.format(serialize_parametrs(self.client_parameters), end=''), encoding="UTF-8"))
            except:
                self.qOut.put(bytes('failed: {0}'.format('12'), encoding="UTF-8"))        
        
        if command[0] == 'start':
            #Обработка нажатия на клавишу "Старт": если не заданы параметры возвращаем ошибку
            if self.client_parameters ==  -1:
                self.qOut.put(bytes('failed: {0}'.format('11'), encoding="UTF-8"))
                return True
            
            self.client = client_thread.client_thread(self.connection, self.client_parameters, self.qOut)
            self.client.start()

        if command[0] == 'stop':
            if self.client is not None:
                self.client.kill()
            return True

        if command[0] == 'exit':
            self.kill_event.set()
            if self.client is not None:
                self.client.kill()
            self.connection.close()
            return False

        if command[0] == 'check':
            print('command check')
            if self.client is not None:
                self.qOut.put(bytes('status: {0}'.format(str(self.client.status), end=''), encoding="UTF-8"))
            else:
                self.qOut.put(bytes('status: {0}'.format('1', end=''), encoding="UTF-8"))
            return True

        if command[0] == 'getLog':
            try:
                self.client.set_output()
            except:
                pass
        return True
