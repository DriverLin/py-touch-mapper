import pickle
import socket
import struct
from turtle import down

import pygame
from pygame.locals import *
from pygame.math import *

DOWN = 0x1
UP = 0x0
DEV_NAME = "rm_kbm"
EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03

REL_X = 0x00
REL_Y = 0x01
REL_WHEEL = 0x08
REL_HWHEEL = 0x06
SYN_REPORT = 0x00

scan2linux = {
    224: 29,
    225: 42,
    226: 56,
    227: 125,
    228: 97,
    229: 54,
    230: 100,
    232: 126,
    4: 30,
    5: 48,
    6: 46,
    7: 32,
    8: 18,
    9: 33,
    10: 34,
    11: 35,
    12: 23,
    13: 36,
    14: 37,
    15: 38,
    16: 50,
    17: 49,
    18: 24,
    19: 25,
    20: 16,
    21: 19,
    22: 31,
    23: 20,
    24: 22,
    25: 47,
    26: 17,
    27: 45,
    28: 21,
    29: 44,
    30: 2,
    31: 3,
    32: 4,
    33: 5,
    34: 6,
    35: 7,
    36: 8,
    37: 9,
    38: 10,
    39: 11,
    40: 28,
    40: 28,
    41: 1,
    41: 1,
    42: 14,
    42: 14,
    43: 15,
    44: 57,
    45: 12,
    45: 12,
    46: 13,
    46: 13,
    47: 26,
    48: 27,
    49: 43,
    50: 43,
    50: 43,
    51: 39,
    52: 40,
    53: 41,
    53: 41,
    54: 51,
    55: 52,
    55: 52,
    56: 53,
    57: 58,
    57: 58,
    58: 59,
    59: 60,
    60: 61,
    61: 62,
    62: 63,
    63: 64,
    64: 65,
    65: 66,
    66: 67,
    67: 68,
    68: 87,
    69: 88,
    70: 99,
    71: 70,
    71: 70,
    72: 119,
    73: 110,
    74: 102,
    75: 104,
    75: 104,
    76: 111,
    76: 111,
    77: 107,
    78: 109,
    78: 109,
    79: 106,
    80: 105,
    81: 108,
    82: 103,
    83: 69,
    83: 69,
    84: 98,
    85: 55,
    86: 74,
    87: 78,
    88: 96,
    88: 96,
    89: 79,
    90: 80,
    91: 81,
    92: 75,
    93: 76,
    94: 77,
    95: 71,
    96: 72,
    97: 73,
    98: 82,
    99: 83,
    99: 83,
    101: 127,
    102: None,
    103: None,
    103: None,
    104: None,
    105: None,
    106: None,
    107: None,
    108: None,
    109: None,
    110: None,
    111: None,
    112: None,
    113: None,
    114: None,
    115: None,
    116: None,
    117: None,
    118: None,
    119: None,
    120: None,
    121: None,
    122: None,
    123: None,
    124: None,
    125: None,
    126: None,
    127: None,
    128: None,
    129: None,
}


mousebtn = {
    "BTN_LEFT": 0x110,
    "BTN_RIGHT": 0x111,
    "BTN_MIDDLE": 0x112,
    "BTN_SIDE": 0x113,
    "BTN_EXTRA": 0x114,
    "BTN_FORWARD": 0x115,
    "BTN_BACK": 0x116,
    "BTN_TASK": 0x117,
}
mousecodemap = [
    None,
    mousebtn['BTN_LEFT'],
    mousebtn['BTN_MIDDLE'],
    mousebtn['BTN_RIGHT'],
    None,
    None,
    mousebtn['BTN_SIDE'],
    mousebtn['BTN_EXTRA'],
]

def pack_events(events,name):
    buffer = (len(events)).to_bytes(1, 'little', signed=False)
    for (type,code,value) in events:
        buffer += struct.pack('<HHi', type, code, value)
    buffer += name.encode()
    return buffer

def unpack_events(buffer):
    print(buffer)
    length = buffer[0]
    events = [
        struct.unpack('<HHi', buffer[i*8+1:i*8+9])
        for i in range(length)
    ]
    name = buffer[length*8+1:].decode()
    return events, name

class sender:
    def __init__(self, addr) -> None:
        print("send all events to :", addr)
        self.targetIp = addr.split(":")[0]
        self.targetPort = int(addr.split(":")[1])
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendArr = (self.targetIp, self.targetPort)

    def sendKey(self, scancode, downup):
        if scan2linux[scancode] != None:
            self.udpSocket.sendto(pack_events([[EV_KEY, scan2linux[scancode], downup]], DEV_NAME), self.sendArr)

    def sendMouseMove(self, x=None, y=None):
        events = []
        if x != None:
            events.append((EV_REL, REL_X, x))
        if y != None:
            events.append((EV_REL, REL_Y, y))
        self.udpSocket.sendto(pack_events(events, DEV_NAME), self.sendArr)

    def sendMouseBTN(self, btn, downup):
        if btn <= 7 and mousecodemap[btn] != None:
            self.udpSocket.sendto(pack_events(
                [[EV_KEY, mousecodemap[btn], downup]], DEV_NAME), self.sendArr)

    def sendWheel(self, value):
        self.udpSocket.sendto(pack_events(
            [[EV_REL, REL_WHEEL, value]], DEV_NAME), self.sendArr)


if __name__ == "__main__":
    senderInstance = sender("192.168.1.64:8888")
    pygame.init()
    screen = pygame.display.set_mode((320, 240), 0, 32)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                senderInstance.sendKey(event.scancode, DOWN)
            elif event.type == KEYUP:
                senderInstance.sendKey(event.scancode, UP)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                senderInstance.sendMouseBTN(event.button, DOWN)
            elif event.type == pygame.MOUSEBUTTONUP:
                senderInstance.sendMouseBTN(event.button, UP)
            elif event.type == pygame.MOUSEMOTION:
                rel = pygame.mouse.get_rel()
                senderInstance.sendMouseMove(
                    x=rel[0] if rel[0] != 0 else None, y=rel[1] if rel[1] != 0 else None)
            elif event.type == pygame.MOUSEWHEEL:
                senderInstance.sendWheel(event.y)
