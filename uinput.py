import os
from fcntl import ioctl
import struct


def ui_ioctl(direction, number, size):
    """
    Compute ioctl request number; see _IOC macro

    direction is direction of data from user perspective
    number is the ioctl number
    size is the number of bytes transferred in the call

    returns the ioctl request number.
    """

    dirs = {
        'R': 2,   # _IOC_READ
        'W': 1,   # _IOC_WRITE
        'RW': 3,  # _IOC_READ | _IOC_WRITE
        'N': 0,   # _IOC_NONE
    }

    typ = ord('U')  # UINPUT_IOCTL_CREATE

    if not 0 <= number < 256:
        raise ValueError

    if not 0 <= typ < 256:
        raise ValueError

    if not 0 <= size < 16384:
        raise ValueError

    return (dirs[direction] << 30) | (size << 16) | (typ << 8) | (number << 0)


EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
SYN_REPORT = 0
UINPUT_MAX_NAME_SIZE = 80  # A null terminator isn't required, all 80 chars can be used.
UI_DEV_CREATE = ui_ioctl('N', 0x01, 0)
UI_DEV_DESTROY = ui_ioctl('N', 0x02, 0)
UI_DEV_SETUP = ui_ioctl('W', 0x03, 2 + 2 + 2 + 2 + UINPUT_MAX_NAME_SIZE + 4)
UI_GET_VERSION = ui_ioctl('R', 0x2d, 4)
UI_SET_EVBIT = ui_ioctl('W', 0x64, 4)
UI_SET_KEYBIT = ui_ioctl('W', 0x65, 4)
UI_SET_RELBIT = ui_ioctl('W', 0x66, 4)

def UI_GET_SYSNAME(n):
    return ui_ioctl('R', 0x2c, n)


class UInput:
    _fd = None

    def __init__(self):
        self._fd = os.open('/dev/uinput', os.O_RDWR)
        self.set_evbit(EV_SYN)
        self.set_evbit(EV_KEY)
        self.set_evbit(EV_REL)
        

    @property
    def version(self):
        buf = bytearray(4)
        ioctl(self._fd, UI_GET_VERSION, buf)
        return struct.unpack('=I', buf)[0]

    def set_evbit(self, bit):
        ioctl(self._fd, UI_SET_EVBIT, bit)

    def set_keybit(self, bit):
        ioctl(self._fd, UI_SET_KEYBIT, bit)
    def set_relbit(self, bit):
        ioctl(self._fd, UI_SET_RELBIT, bit)


    def dev_setup(self, bustype, vendor, product, version, name, ff_effects_max):
        name_enc = name.encode()
        if len(name_enc) > UINPUT_MAX_NAME_SIZE:
            raise ValueError('Name too long')
        buf = struct.pack('=HHHH80sI', bustype, vendor, product, version, name_enc, ff_effects_max)
        ioctl(self._fd, UI_DEV_SETUP, buf, False)

    def create_dev(self):
        ioctl(self._fd, UI_DEV_CREATE, 0)

    def destroy_dev(self):
        ioctl(self._fd, UI_DEV_DESTROY, 0)

    def get_sysname(self):
        buf = bytearray(65)
        ioctl(self._fd, UI_GET_SYSNAME(65), buf)
        return buf.rstrip(b'\x00').decode()

    def send_event(self, time, type, code, value):
        # XXX time is "struct timeval" (long sec + long usec). Find out what it's for and implement it.
        buf = struct.pack('=QQHHi', 0, 0, type, code, value)

        if os.write(self._fd, buf) != 24:
            raise OSError

    def key_press(self, k):
        self.send_event(None, EV_KEY, k, 1)

    def key_release(self, k):
        self.send_event(None, EV_KEY, k, 0)

    def syn(self):
        self.send_event(None, EV_SYN, SYN_REPORT, 0)

    def __del__(self):
        if self._fd:
            os.close(self._fd)
            self._fd = None
