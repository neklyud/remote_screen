import threading
import subprocess
import os
import signal
import sys

def output_reader(proc, connection, q, event):
    try:
        for line in iter(proc.stdout.readline, b''):
            print(line)
            if event.is_set():
                q.put(bytes('log: {0}'.format(line.decode('utf-8'), end=''), encoding="UTF-8"),timeout=0.15)                
            proc.stdout.flush()
    except ValueError:
        pass

def make_running_command(params):
    command = 'python -u ' + str(params[0]) + ' --dataset_name=' + '"' + str(params[1]) + '" ' + '--batch_siz='+str(params[2]) + ' --lr=' + str(params[3])
    return command.split()

class output_status:
    def __init__(self):
        self.status = 1
    def get(self):
        return self.status

class client_thread(threading.Thread):
    
    def __init__(self, connection, params, q):
        threading.Thread.__init__(self)
        self.connection = connection
        os.environ["CUDA_VISIBLE_DEVICES"]="0"
        self.q = q
        self.params = params
        self.status = 1
        self.proc = subprocess.Popen(make_running_command(self.params),stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=13, shell=False)
        self.output_event = threading.Event()

    def run(self):
        print("client thread is running...")
        output_reader(self.proc, self.connection, self.q, self.output_event)
    
    def kill(self):
        self.q.task_done()
        self.output_event.clear()
        self.proc.stderr.close()
        self.proc.stdout.close()
        self.proc.stdin.close()
        self.proc.terminate()
        self.proc.kill()
        self.killed = True

    def set_output(self):
        self.output_event.set()
