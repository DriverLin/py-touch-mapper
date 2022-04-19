
import os
from subprocess import *

if __name__ == "__main__":
    FIFO_PATH = '/data/data/com.termux/files/home/py-touch-mapper/pipe-test/fifo.pipe'
    if os.path.exists(FIFO_PATH):
        os.unlink(FIFO_PATH)
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)

    fd = os.open(FIFO_PATH, os.O_RDONLY)
    while True:
        line = os.read(fd, 1024)
        if not line:
            continue
        print(line)
