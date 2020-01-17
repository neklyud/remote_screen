import threading
import subprocess
import os

def output_reader(proc, connection, q):
    for line in iter(proc.stdout.readline, b''):
        try:
            #connection.send(bytes('got line: {0}'.format(line.decode('utf-8'), end=''), encoding="UTF-8"))
            q.put(bytes('got line: {0}'.format(line.decode('utf-8'), end=''), encoding="UTF-8"))
        except IOError:
            return
        #print('got line: {0}'.format(line.decode('utf-8')), end='')
        proc.stdout.flush()

class client_thread(threading.Thread):
    def __init__(self, connection, path, q):
        threading.Thread.__init__(self)
        self.connection = connection
        os.environ["CUDA_VISIBLE_DEVICES"]="0"
        self.proc = subprocess.Popen(['python','-u', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=13)
        self.q = q
    def run(self):
        print("client thread is running...")
        output_reader(self.proc, self.connection, self.q)
    def kill(self):
        self.q.task_done()
        self.proc.kill() 
        self.killed = True

