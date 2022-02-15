from fcntl import ioctl
import ctypes
import os


class input_absinfo(ctypes.Structure):
    _fields_ = [
        ("value", ctypes.c_int32),
        ("minimum", ctypes.c_int32),
        ("maximum", ctypes.c_int32),
        ("fuzz", ctypes.c_int32),
        ("flat", ctypes.c_int32),
        ("resolution", ctypes.c_int32),
    ]

    def __repr__(self):
        return "input_absinfo(value={}, minimum={}, maximum={}, fuzz={}, flat={} resolution={}) # object at {}".format(
            self.value,
            self.minimum,
            self.maximum,
            self.fuzz,
            self.flat,
            self.resolution,
            hex(id(self)),
        )


_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS


def ui_ioctl(direction, number, size):
    """
    Compute ioctl request number; see _IOC macro
    direction is direction of data from user perspective
    number is the ioctl number
    size is the number of bytes transferred in the call
    returns the ioctl request number.
    """
    dirs = {
        "R": 2,  # _IOC_READ
        "W": 1,  # _IOC_WRITE
        "RW": 3,  # _IOC_READ | _IOC_WRITE
        "N": 0,  # _IOC_NONE
    }

    typ = ord("U")  # UINPUT_IOCTL_CREATE

    if not 0 <= number < 256:
        raise ValueError

    if not 0 <= typ < 256:
        raise ValueError

    if not 0 <= size < 16384:
        raise ValueError

    return (dirs[direction] << 30) | (size << 16) | (typ << 8) | (number << 0)


def UI_GET_SYSNAME(n):
    return ui_ioctl("R", 0x2C, n)


def _IOC_TYPECHECK(t):
    return ctypes.sizeof(t)


def _IOC(dir_, type_, nr, size):
    return (
        ctypes.c_int32(dir_ << _IOC_DIRSHIFT).value
        | ctypes.c_int32(ord(type_) << _IOC_TYPESHIFT).value
        | ctypes.c_int32(nr << _IOC_NRSHIFT).value
        | ctypes.c_int32(size << _IOC_SIZESHIFT).value
    )


def _IOR(type_, nr, size):
    return _IOC(_IOC_READ, type_, nr, _IOC_TYPECHECK(size))


EVIOCGABS = lambda abs: _IOR("E", 0x40 + abs, input_absinfo)


def get_absinfo_from_fd(fd, absIndex):
    absinfo = input_absinfo()
    r = ioctl(fd, EVIOCGABS(absIndex), absinfo)
    return r, absinfo

def get_absname_from_fd(fd):
    buf = bytearray(256)
    EVIOCGNAME = lambda length: _IOC(_IOC_READ, "E", 0x06, length)
    ioctl(fd, EVIOCGNAME(256), buf)
    return buf.strip(b"\x00").decode("utf-8")


def getABSRanges(path):
    fd = open(path, "rb")
    absRange = {}
    for i in range(64):
        r, info = get_absinfo_from_fd(fd, i)
        if info.minimum == info.maximum:
            continue
        else:
            absRange[i] = (info.minimum, info.maximum)
    fd.close()
    return absRange


def getABSName(path):
    fd = os.open(path, os.O_RDWR)
    name = get_absname_from_fd(fd)
    os.close(fd)
    return name
