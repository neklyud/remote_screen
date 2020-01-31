import time
import threading
import subprocess
import os
import queue


def output_reader(proc, q, event, kill):
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                continue
            if event.is_set():
                if not q.full():
                    q.put(bytes('log: {0}'.format(line.decode('utf-8'), end=''), encoding="UTF-8"))
            proc.stdout.flush()
            #for line in iter(proc.stdout.readline, b''):
            #    if event.is_set():
            #        if not q.full():
            #            q.put(bytes('log: {0}'.format(line.decode('utf-8'), end=''), encoding="UTF-8"))
            #    proc.stdout.flush()
    except ValueError:
        pass

def make_running_command(params):
    try:
        command = 'python -u ' + str(params[0]) + ' --dataset_name=' + '"' + str(params[1]) + '" ' + '--batch_siz='+str(params[2]) + ' --lr=' + str(params[3])
        return command.split()
    except:
        return ['echo']

class output_status:
    def __init__(self):
        self.status = 1
    def get(self):
        return self.status

class client_thread(threading.Thread):
    
    def __init__(self, params = None, q = None):
        threading.Thread.__init__(self)
        os.environ["CUDA_VISIBLE_DEVICES"]="1"
        self.q = queue.Queue(maxsize=20)
        self.params = params
        self.status = 0
        self.output_event = threading.Event()
        self.kill_event = threading.Event()
    def run(self):
        print("client thread is running...")
        print(make_running_command(self.params))
        while True:
            time.sleep(0.1)
            if self.params is None:
                continue
            p = make_running_command(self.params)
            if self.status == 1:
                self.proc = subprocess.Popen(make_running_command(self.params),stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
                output_reader(self.proc, self.q, self.output_event, self.kill_event)

    
    def stop_learning(self):
        self.status = 0
        self.q.task_done()
        self.output_event.clear()
        self.kill_event.set()
        self.proc.stderr.close()
        self.proc.stdout.close()
        self.proc.stdin.close()
        self.proc.terminate()
        self.proc.kill()
        self.killed = True

    def kill(self):
        self.output_event.clear()
        self.q.queue.clear()

    def set_output(self):
        self.output_event.set()

    def reset_outout(self):
        self.output_event.clear()

    def set_status(self, val):
        self.status = val

client = client_thread()
