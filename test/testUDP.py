import os
import socket
import threading
from time import sleep, time

SERVER_ADDR = "./testUDP.sock"

def server():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    if os.path.exists(SERVER_ADDR):
        os.unlink(SERVER_ADDR)
    s.bind(SERVER_ADDR)
    result = []
    while True:
        data,__ = s.recvfrom(32)
        now = time()
        result.append(now - float(data.decode()))
        if float(data.decode()) == 0:
            s.close()
            break    
    for i in result:
        print( i)


def client():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.connect(SERVER_ADDR)
    s.sendto(str(time()).encode(), SERVER_ADDR)
    s.close()

def stop():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.connect(SERVER_ADDR)
    s.sendto(str(0).encode(), SERVER_ADDR)
    s.close()


if __name__ == "__main__":
    threading.Thread(target=server).start()
    sleep(0.5)
    for i in range(100):
        client()
        # sleep(0.1)
    stop()


