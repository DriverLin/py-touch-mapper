import queue
import sys
import os
import json
import ctypes
import struct
import sys
import time
import threading
import fcntl
from abs_get import get_absinfo,get_absname
import ioctl_opt
import random
import curses

EVIOCGRAB = lambda len: ioctl_opt.IOW(ord("E"), 0x90, ctypes.c_int)

EVENT_FORMAT = "llHHI"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)
EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03

DOWN = 0x1
UP = 0x0

SYN_REPORT = 0x00


eventQueue = queue.Queue()
stopFlag = False
dpadRanges = {}
absRanges = {}

stdscr = curses.initscr()
stdscr.nodelay(1)
curses.start_color()
curses.noecho()
curses.cbreak()


def printScr(msg="", x=0, y=7):
    global stdscr
    stdscr.addstr(y, x, str(msg) + "\t\t\t")
    stdscr.refresh()


def joyStickchecker(events):
    global eventQueue
    for event in events:
        eventQueue.put(event)
    return stopFlag


def devReader(path="", handeler=None):
    """path:设备路径
    handeler:事件处理器
    exclusive:是否独占
    mode:运行标志 模式 直接传递给事件处理器
    switchMode:切换模式函数
    返回 thread 外部join()"""

    def readFunc():
        with open(path, "rb") as f:
            buffer = []
            fcntl.ioctl(f, EVIOCGRAB(1), True)
            while True:
                byte = f.read(EVENT_SIZE)
                e_sec, e_usec, e_type, e_code, e_val = struct.unpack(EVENT_FORMAT, byte)
                if e_type == EV_SYN and e_code == SYN_REPORT and e_val == 0:
                    if handeler(buffer):
                        break
                    buffer.clear()
                else:
                    buffer.append(
                        (
                            e_type,
                            e_code,
                            e_val if e_val <= 0x7FFFFFFF else e_val - 0x100000000,
                        )
                    )

    thread = threading.Thread(target=readFunc)
    thread.start()
    return thread


def getEvent(type=EV_KEY):
    while True:
        (_type, code, value) = eventQueue.get()
        if _type == type:
            return (type, code, value)


def userInputKey(keyName=" "):
    while True:
        try:
            printScr(msg=f"please press {keyName}")
            ev_key, down_code, down_updown = getEvent(EV_KEY)
            ev_key, up_code, up_updown = getEvent(EV_KEY)
            assert down_updown == DOWN
            assert up_updown == UP
            assert down_code == up_code
            return down_code
        except Exception as e:
            printScr(msg="error:" + e.__str__())
            continue


def getDPAD():
    dpadMap = {}
    mapped = []
    if len(dpadRanges.keys()) == 0:
        for kname in ["DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT"]:
            printScr(msg=f"please press {kname}")
            dpadMap[kname] = userInputKey(kname)
    else:
        for kname in ["DPAD_UP", "DPAD_RIGHT"]:
            printScr(msg=f"please press {kname}")
            checked = False
            while not checked:
                ev_abs, code, value = getEvent(EV_ABS)
                if (
                    code in dpadRanges
                    and (value == 1 or value == -1)
                    and (code not in mapped)
                ):
                    dpadMap[kname] = [code, value]
                    checked = True
                    mapped.append(code)
    return dpadMap


def printABS(absVals):
    for index, axis in enumerate(absRanges):
        axisRange = absRanges[axis][1] - absRanges[axis][0]
        percent = int((absVals[axis] - absRanges[axis][0]) * 40 / axisRange)
        stausBar = "◁{}[]{}▷  ".format(percent * "=", (40 - percent) * "=")
        stausBar = stausBar[:4] + "|" + stausBar[4:40] + "|" + stausBar[40:]
        printScr(stausBar, 0, index)


def getABSMap():
    lastValue = {
        axis: (absRanges[axis][1] + absRanges[axis][0]) / 2 for axis in absRanges
    }  # 仅有axis没有trigger
    selectedAxis = []
    axisInfo = {
        "LS_X": None,
        "LS_Y": None,
        "RS_X": None,
        "RS_Y": None,
        "LT": None,
        "RT": None,
    }
    if len(absRanges.keys()) == 6:
        printABS(lastValue)
        for trigger in ["LT", "RT"]:
            printScr(msg="please pull {}".format(trigger))
            checked = False
            rangeRecoard = {
                axis: [absRanges[axis][1], absRanges[axis][0]] for axis in absRanges
            }
            while not checked:
                ev_abs, code, value = getEvent(EV_ABS)
                if code not in absRanges:
                    continue
                lastValue[code] = value
                [lastMin, lastMax] = rangeRecoard[code]
                newMin = min(lastMin, value)
                newMax = max(lastMax, value)
                rangeRecoard[code] = [newMin, newMax]
                for axis in absRanges:
                    currentDis = rangeRecoard[axis][1] - rangeRecoard[axis][0]
                    maxDis = absRanges[axis][1] - absRanges[axis][0]
                    if currentDis / maxDis > 0.99:
                        if axis not in selectedAxis:
                            axisInfo[trigger] = axis
                            checked = True
                            selectedAxis.append(axis)
                printABS(lastValue)
    else:  # 仅有四个轴 switch pro LT,RT为按键
        for trigger in ["LT", "RT"]:
            printScr(msg="please press {}".format(trigger))
            axisInfo[trigger] = userInputKey(trigger)

    printABS(lastValue)
    for lr in ["LS", "RS"]:
        for direction in ["UP", "RIGHT"]:
            printScr(msg="please pull {}  {}".format(lr, direction))
            checked = False
            while not checked:
                ev_abs, code, value = getEvent(EV_ABS)
                lastValue[code] = value
                for axis in absRanges:
                    (minimum, maximum) = absRanges[axis]
                    minDis = (lastValue[axis] - minimum) / (maximum - minimum)
                    maxDis = (maximum - lastValue[axis]) / (maximum - minimum)
                    if minDis < 0.05 and maxDis > 0.95:  # min (=[]========) max
                        x_name = "Y" if direction == "UP" else "X"
                        x_name = f"{lr}_{x_name}"
                        if axis not in selectedAxis:
                            axisInfo[x_name] = [axis,False if direction == "UP" else True]
                            checked = True
                            selectedAxis.append(axis)
                    elif minDis > 0.95 and maxDis < 0.05:  # min (========[]=) max
                        x_name = "Y" if direction == "UP" else "X"
                        x_name = f"{lr}_{x_name}"
                        if axis not in selectedAxis:
                            axisInfo[x_name] = [axis,True if direction == "UP" else False]
                            checked = True
                            selectedAxis.append(axis)
                printABS(lastValue)
    return axisInfo


def getABSRanges(path):
    fp = open(path, "rb")
    absRange = {}
    for i in range(64):
        r, info = get_absinfo(fp, i)
        if info.minimum == info.maximum:
            continue
        else:
            absRange[i] = (info.minimum, info.maximum)
    fp.close()
    return absRange

def getAbsName(path):
    fp = open(path, "rb")
    name = get_absname(fp)
    fp.close()
    return name




if __name__ == "__main__":
    if os.geteuid() != 0:
        print("请以root权限运行")
        exit(1)
    if len(sys.argv) != 2:
        print("args error! , except 2 got {}".format(len(sys.argv)))
        exit(2)

    jsInfo = {
        "DEADZONE": {
            "LS": [0.5 - 0.1, 0.5 + 0.1],
            "RS": [0.5 - 0.04, 0.5 + 0.04],
        },
        "ABS": {},
        "BTN": {},
        "MAP_KEYBOARD": {
            "BTN_LT_2": "BTN_RIGHT",
            "BTN_RT_2": "BTN_LEFT",
            "BTN_DPAD_UP": "KEY_UP",
            "BTN_DPAD_LEFT": "KEY_LEFT",
            "BTN_DPAD_RIGHT": "KEY_RIGHT",
            "BTN_DPAD_DOWN": "KEY_DOWN",
            "BTN_A": "KEY_ENTER",
            "BTN_B": "KEY_BACK",
            "BTN_SELECT": "KEY_COMPOSE",
            "BTN_THUMBL": "KEY_HOME",
        },
    }

    jsPath = "/dev/input/event{}".format(sys.argv[1])

    name = getAbsName(jsPath)
    printScr(name)
    exit()

    readResult = getABSRanges(jsPath)
    for index in readResult:
        (minimum, maximum) = readResult[index]
        if minimum == -1 and maximum == 1:
            dpadRanges[index] = (minimum, maximum)
        else:
            absRanges[index] = (minimum, maximum)
    # print(absRanges, dpadRanges)

    reader = devReader(jsPath, joyStickchecker)

    dpadResult = getDPAD()
    printScr(msg=json.dumps(dpadResult), x=0, y=8)
    if len(dpadRanges.keys()) == 0:
        for kname in dpadResult:
            jsInfo["BTN"][int(dpadResult[kname])] = "BTN_" + kname
    else:
        code, rev = dpadResult["DPAD_UP"]
        jsInfo["ABS"][int(code)] = {
            "name": "HAT0Y",
            "range": [dpadRanges[code][0], dpadRanges[code][1]],
            "reverse": rev == 1,
        }
        code, rev = dpadResult["DPAD_RIGHT"]
        jsInfo["ABS"][int(code)] = {
            "name": "HAT0X",
            "range": [dpadRanges[code][0], dpadRanges[code][1]],
            "reverse": rev == -1,
        }
    for keyname in [
        "A",
        "B",
        "X",
        "Y",
        "LS",
        "RS",
        "LB",
        "RB",
        "SELECT",
        "START",
        "HOME",
    ]:
        code = userInputKey(keyname)
        jsInfo["BTN"][int(code)] = "BTN_" + keyname

    absMapresult = getABSMap()
    printScr(msg=json.dumps(absMapresult), x=0, y=9)
    
    for axis in ["LS", "RS"]:
        for direction in ["X", "Y"]:
            axisname = f"{axis}_{direction}"
            code,rev = absMapresult[axisname]
            jsInfo["ABS"][int(code)] = {
                "name": axisname,
                "range": [ absRanges[code][0]  , absRanges[code][1]],
                "reverse": rev,
            }
        for axisname in ["LT","RT"]:
            code = absMapresult[axisname]
            if len(absRanges.keys()) == 6:
                jsInfo["ABS"][int(code)] = {
                    "name": axisname,
                    "range": [ absRanges[code][0]  , absRanges[code][1]],
                    "reverse": False,
                }
            else:
                jsInfo["BTN"][int(code)] = "BTN_" + axisname

    with open("./out.json",'w') as f:
        f.write(json.dumps(jsInfo, indent=4))

    stopFlag = True
    printScr(msg="press any key to exit", x=0, y=10)
