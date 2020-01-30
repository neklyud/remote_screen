import copy
import re


def send(connection, data):
    try:
        n_bytes = connection.send(data)
    except BrokenPipeError:
        pass

def split_num_str(string):
    num = re.search(r'[0-9]+', string)
    chrs = re.search(r'[a-zA-Z]+', string)
    return num.group(0), chrs.group(0)


def recv(connection):
    try:
        msg_len = str(connection.recv(4).decode("UTF-8"))
        if not msg_len:
            return -1
        
        try:
            msg_len = int(msg_len)
        except ValueError:
            msg = str(copy.copy(split_num_str(msg_len)[1]))
            msg_len = int(split_num_str(msg_len)[0])
            msg += str(connection.recv(msg_len - len(msg)).decode("UTF-8"))
            return msg.split()

        msg = connection.recv(msg_len).decode("UTF-8")
        return msg.split()
    except ConnectionResetError:
        return -1
