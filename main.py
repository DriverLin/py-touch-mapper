import sys
import os
import json
import ctypes
import struct
import sys
import time
import threading
import fcntl
import ioctl_opt
import random

eventPacker = lambda e_type, e_code, e_value: struct.pack(
    EVENT_FORMAT, 0, 0, e_type, e_code, e_value
)
getRand = lambda: random.randint(0, 20)


DOWN = 0x1
UP = 0x0
MOVE_FLAG = 0x0
RELEASE_FLAG = 0x2
REQURIE_FLAG = 0x1
WHEEL_REQUIRE = 0x3
MOUSE_REQUIRE = 0x4

ABS_MT_POSITION_X = 0x35
ABS_MT_POSITION_Y = 0x36
ABS_MT_SLOT = 0x2F
ABS_MT_TRACKING_ID = 0x39
EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
REL_X = 0x00
REL_Y = 0x01

SYN_REPORT = 0x00

BTN_TOUCH = 0x14A
KEY_GRAVE = 0x29
BTN_MOUSE = 0x110


EVENT_FORMAT = "llHHI"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

SYN_EVENT = eventPacker(EV_SYN, SYN_REPORT, 0x0)
EVIOCGNAME = lambda len: ioctl_opt.IOC(ioctl_opt.IOC_READ, ord("E"), 0x06, len)
EVIOCGRAB = lambda len: ioctl_opt.IOW(ord("E"), 0x90, ctypes.c_int)

HAT_D_U = {
    "0.5_1.0": (1, DOWN),
    "0.5_0.0": (0, DOWN),
    "1.0_0.5": (1, UP),
    "0.0_0.5": (0, UP),
}

HAT0_KEYNAME = {
    "HAT0X": ["BTN_DPAD_LEFT", "BTN_DPAD_RIGHT"],
    "HAT0Y": ["BTN_DPAD_UP", "BTN_DPAD_DOWN"],
}


LR_RT_VALUEMAP = {
    "LT": [(x / 5 - 0.01, f"BTN_LT_{x}") for x in range(1, 6)],
    "RT": [(x / 5 - 0.01, f"BTN_RT_{x}") for x in range(1, 6)],
}


IN_DEADZONE = -1

keynamemapval = {
    "KEY_RESERVED": 0,
    "KEY_ESC": 1,
    "KEY_1": 2,
    "KEY_2": 3,
    "KEY_3": 4,
    "KEY_4": 5,
    "KEY_5": 6,
    "KEY_6": 7,
    "KEY_7": 8,
    "KEY_8": 9,
    "KEY_9": 10,
    "KEY_0": 11,
    "KEY_MINUS": 12,
    "KEY_EQUAL": 13,
    "KEY_BACKSPACE": 14,
    "KEY_TAB": 15,
    "KEY_Q": 16,
    "KEY_W": 17,
    "KEY_E": 18,
    "KEY_R": 19,
    "KEY_T": 20,
    "KEY_Y": 21,
    "KEY_U": 22,
    "KEY_I": 23,
    "KEY_O": 24,
    "KEY_P": 25,
    "KEY_LEFTBRACE": 26,
    "KEY_RIGHTBRACE": 27,
    "KEY_ENTER": 28,
    "KEY_LEFTCTRL": 29,
    "KEY_A": 30,
    "KEY_S": 31,
    "KEY_D": 32,
    "KEY_F": 33,
    "KEY_G": 34,
    "KEY_H": 35,
    "KEY_J": 36,
    "KEY_K": 37,
    "KEY_L": 38,
    "KEY_SEMICOLON": 39,
    "KEY_APOSTROPHE": 40,
    "KEY_GRAVE": 41,
    "KEY_LEFTSHIFT": 42,
    "KEY_BACKSLASH": 43,
    "KEY_Z": 44,
    "KEY_X": 45,
    "KEY_C": 46,
    "KEY_V": 47,
    "KEY_B": 48,
    "KEY_N": 49,
    "KEY_M": 50,
    "KEY_COMMA": 51,
    "KEY_DOT": 52,
    "KEY_SLASH": 53,
    "KEY_RIGHTSHIFT": 54,
    "KEY_KPASTERISK": 55,
    "KEY_LEFTALT": 56,
    "KEY_SPACE": 57,
    "KEY_CAPSLOCK": 58,
    "KEY_F1": 59,
    "KEY_F2": 60,
    "KEY_F3": 61,
    "KEY_F4": 62,
    "KEY_F5": 63,
    "KEY_F6": 64,
    "KEY_F7": 65,
    "KEY_F8": 66,
    "KEY_F9": 67,
    "KEY_F10": 68,
    "KEY_NUMLOCK": 69,
    "KEY_SCROLLLOCK": 70,
    "KEY_F11": 87,
    "KEY_F12": 88,
    "KEY_HOME": 102,
    "KEY_UP": 103,
    "KEY_PAGEUP": 104,
    "KEY_LEFT": 105,
    "KEY_RIGHT": 106,
    "KEY_END": 107,
    "KEY_DOWN": 108,
    "KEY_PAGEDOWN": 109,
    "KEY_INSERT": 110,
    "KEY_DELETE": 111,
    "BTN_LEFT": 0x110,
    "BTN_RIGHT": 0x111,
    "BTN_MIDDLE": 0x112,
    "BTN_SIDE": 0x113,
    "BTN_EXTRA": 0x114,
    "BTN_FORWARD": 0x115,
    "BTN_BACK": 0x116,
    "BTN_TASK": 0x117,
}
printMap = {
    0x4: "MOUSE_REQUIRE",
    0x3: "WHEEL_REQUIRE",
    0x2: "RELEASE_FLAG",
    0x1: "REQURIE_FLAG",
    0x0: "MOVE_FLAG",
}


class touchController:
    def __init__(self, path) -> None:
        self.path = path
        self.fp = open(self.path, "wb")
        # 上次触摸id
        self.last_touch_id = -1
        # 触摸点数量
        self.allocatedID_num = 0
        # 分配的触摸点id
        self.touch_id_list = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # 鼠标分配的触摸点id
        # switch between 0 and 1
        self.mouse_id = 0
        self.lock = threading.Lock()

    def fpcheck(self):
        if self.fp.closed:
            self.fp = open(self.path, "wb")

    # 锁！！！！
    def postEvent(self, type, uncertainId, x, y):
        self.lock.acquire()
        # self.fpcheck()
        trueId = uncertainId
        if type == MOVE_FLAG and uncertainId != -1:
            if self.last_touch_id != uncertainId:
                self.fp.write(eventPacker(EV_ABS, ABS_MT_SLOT, uncertainId))
                self.last_touch_id = uncertainId
            # 虽然负数pack异常，但是触屏这里不需要
            self.fp.write(eventPacker(EV_ABS, ABS_MT_POSITION_X, x & 0xFFFFFFFF))
            self.fp.write(eventPacker(EV_ABS, ABS_MT_POSITION_Y, y & 0xFFFFFFFF))
            self.fp.write(SYN_EVENT)
            self.fp.flush()

        elif type == RELEASE_FLAG and uncertainId != -1:
            trueId = -1
            self.touch_id_list[uncertainId] = 0
            self.allocatedID_num -= 1

            if self.last_touch_id != uncertainId:
                self.fp.write(eventPacker(EV_ABS, ABS_MT_SLOT, uncertainId))
                self.last_touch_id = uncertainId

            self.fp.write(eventPacker(EV_ABS, ABS_MT_TRACKING_ID, 0xFFFFFFFF))
            if self.allocatedID_num == 0:
                self.fp.write(eventPacker(EV_KEY, BTN_TOUCH, UP))
            self.fp.write(SYN_EVENT)
            self.fp.flush()
        else:
            if type == MOUSE_REQUIRE:
                self.mouse_id = 1 if self.mouse_id == 0 else 0
                trueId = self.mouse_id
            elif type == WHEEL_REQUIRE:
                trueId = 2
            elif type == REQURIE_FLAG:
                for i in range(3, 10):
                    if self.touch_id_list[i] == 0:
                        trueId = i
                        break
            if trueId == -1:
                # 没有空余的触摸点
                self.lock.release()
                return -1

            self.touch_id_list[trueId] = 1
            self.allocatedID_num += 1
            self.last_touch_id = trueId

            self.fp.write(eventPacker(EV_ABS, ABS_MT_SLOT, trueId))
            self.fp.write(eventPacker(EV_ABS, ABS_MT_TRACKING_ID, trueId))
            if self.allocatedID_num == 1:
                self.fp.write(eventPacker(EV_KEY, BTN_TOUCH, DOWN))
            self.fp.write(eventPacker(EV_ABS, ABS_MT_POSITION_X, x & 0xFFFFFFFF))
            self.fp.write(eventPacker(EV_ABS, ABS_MT_POSITION_Y, y & 0xFFFFFFFF))
            self.fp.write(SYN_EVENT)
            self.fp.flush()
        # print("(",printMap[type],"\tudi=",uncertainId ,"\t[", x,"," , y,"]" , ") => ",trueId)
        self.lock.release()
        return trueId


global_exclusive_flag = False


def translate_keyname_keycode(keyname):
    if keyname in keynamemapval:#在映射列表中的
        return keynamemapval[keyname]
    elif keyname.startswith("BTN_"):#不在映射列表中 且以BTN_开头 视为手柄按键映射 直接用name作为keycode
        return keyname
    else:
        print("ERROR KEYNAME ", keyname)
        return 0


class eventHandeler:
    def __init__(
        self, map_config, touchController, reportRate=250, jsViewRate=250, jsInfo=None
    ) -> None:
        self.jsInfo = jsInfo  # 手柄的配置信息 包含数值范围 按键信息等
        self.abs_last = {
            "HAT0X": 0.5,
            "HAT0Y": 0.5,
            "LT": 0,
            "RT": 0,
            "LS_X": 0.5,
            "LS_Y": 0.5,
            "RS_X": 0.5,
            "RS_Y": 0.5,
        }  # 方向键的值
        self.reportRate = 1 / reportRate
        self.jsViewRate = 1 / jsViewRate
        self.js_switch_key_down = UP
        self.exit_flag = False  # 退出标志 用于停止内部线程
        self.mouseLock = threading.Lock()  # 由于鼠标操作来源不唯一(定时释放和事件驱动的移动)所以需要锁
        self.wheelLock = threading.Lock()  # 左移动摇杆  可以同时用键盘和手柄触发
        self.SWITCH_KEY = translate_keyname_keycode(map_config["MOUSE"]["SWITCH_KEY"])
        self.switch_key_down = False
        self.keyMap = {
            translate_keyname_keycode(keyname): map_config["KEY_MAPS"][keyname]
            for keyname in map_config["KEY_MAPS"]
        }

        [wheel_x, wheel_y] = map_config["WHEEL"]["POS"]
        self.wheel_range = map_config["WHEEL"]["RANGE"]
        self.wheelMap = [
            [wheel_x - self.wheel_range, wheel_y - self.wheel_range],
            [wheel_x, wheel_y - self.wheel_range],
            [wheel_x + self.wheel_range, wheel_y - self.wheel_range],
            [wheel_x - self.wheel_range, wheel_y],
            [wheel_x, wheel_y],
            [wheel_x + self.wheel_range, wheel_y],
            [wheel_x - self.wheel_range, wheel_y + self.wheel_range],
            [wheel_x, wheel_y + self.wheel_range],
            [wheel_x + self.wheel_range, wheel_y + self.wheel_range],
        ]
        self.wheel_wasd = [
            translate_keyname_keycode(keyname)
            for keyname in map_config["WHEEL"]["WASD"]
        ]

        self.touchController = touchController

        self.keyMappingDatas = {}  # 存储每个按键对应的action执行中需要的数据

        self.mouseTouchID = -1

        self.wheelTouchID = -1

        [self.realtiveX, self.realtiveY] = map_config["MOUSE"]["POS"]
        [self.mouseStartX, self.mouseStartY] = map_config["MOUSE"]["POS"]
        [self.screenSizeX, self.screenSizeY] = map_config["SCREEN"]["SIZE"]
        [self.mouseSpeedX, self.mouseSpeedY] = map_config["MOUSE"]["SPEED"]
        self.mouseNotMoveCount = 0

        # 修改wheelTarget 自动控制移动以及释放
        self.wheel_satuse = [0, 0, 0, 0]
        self.wheelTarget = (self.wheelMap[4][0], self.wheelMap[4][1])

        def wheelThreadFunc():
            wheelNow = (self.wheelMap[4][0], self.wheelMap[4][1])
            while not self.exit_flag:
                # 等于中心 直接释放
                if self.wheelTarget == self.wheelMap[4]:
                    self.handelWheelMoveAction(type=RELEASE_FLAG)
                elif wheelNow != self.wheelTarget:
                    restX, restY = (
                        self.wheelTarget[0] - wheelNow[0],
                        self.wheelTarget[1] - wheelNow[1],
                    )
                    targetX = (
                        self.wheelTarget[0]
                        if abs(restX) < 30
                        else wheelNow[0] + int((10 + getRand()) * restX / abs(restX))
                    )
                    targetY = (
                        self.wheelTarget[1]
                        if abs(restY) < 30
                        else wheelNow[1] + int((10 + getRand()) * restY / abs(restY))
                    )
                    wheelNow = (targetX, targetY)
                    self.handelWheelMoveAction(targetX=targetX, targetY=targetY)
                time.sleep(self.reportRate)

        def mouseAutoRelease():
            while not self.exit_flag:
                if self.mouseTouchID != -1:
                    if self.mouseNotMoveCount > 100:
                        self.handelMouseMoveAction(type=RELEASE_FLAG)
                    else:
                        self.mouseNotMoveCount += 1
                time.sleep(0.004)  # 0.4秒鼠标没有移动 则释放

        def jsMoveView():
            while not self.exit_flag:
                if self.abs_last["RS_X"] == 0.5 and self.abs_last["RS_Y"] == 0.5:
                    pass
                else:
                    speedX = (self.abs_last["RS_X"] - 0.5) * 2 * 24
                    speedY = (self.abs_last["RS_Y"] - 0.5) * 2 * 24
                    self.handelMouseMoveAction(int(speedX), int(speedY))
                time.sleep(self.jsViewRate)

        threading.Thread(target=wheelThreadFunc).start()
        threading.Thread(target=mouseAutoRelease).start()
        threading.Thread(target=jsMoveView).start()

    def destroy(self):
        self.exit_flag = True

    def handelWheelMoveAction(self, targetX=-1, targetY=-1, type=None):
        if type == None:
            if targetX != -1 and targetY != -1:
                self.wheelLock.acquire()
                if self.wheelTouchID == -1:
                    self.wheelTouchID = self.touchController.postEvent(
                        WHEEL_REQUIRE, -1, self.wheelMap[4][0], self.wheelMap[4][1]
                    )
                self.touchController.postEvent(
                    MOVE_FLAG, self.wheelTouchID, targetX, targetY
                )
                self.wheelLock.release()

        elif type == RELEASE_FLAG:
            if self.wheelTouchID != -1:
                self.wheelLock.acquire()
                self.wheelTouchID = self.touchController.postEvent(
                    RELEASE_FLAG, self.wheelTouchID, 0, 0
                )
                self.wheelLock.release()

    def handelMouseMoveAction(self, offsetX=0, offsetY=0, type=None):
        self.mouseLock.acquire()
        if type == None and (offsetX != 0 or offsetY != 0):
            x = offsetX * self.mouseSpeedX
            y = offsetY * self.mouseSpeedY
            self.mouseNotMoveCount = 0
            # 计算映射坐标
            self.realtiveX -= y
            self.realtiveY += x
            # 如果触摸ID为-1即没有按下 或 映射坐标超出屏幕范围
            if (
                self.mouseTouchID == -1
                or self.realtiveX < 10
                or self.realtiveX > self.screenSizeX - 10
                or self.realtiveY < 10
                or self.realtiveY > self.screenSizeY - 10
            ):
                # 释放触摸  一种情况是第一次申请，ID=-1 不响应释放 另一种情况是触及边界 正常释放
                self.realtiveX = self.mouseStartX + getRand()
                self.realtiveY = self.mouseStartY + getRand()

                self.touchController.postEvent(RELEASE_FLAG, self.mouseTouchID, 0, 0)
                # 申请触摸ID 随机初始偏移量
                self.mouseTouchID = self.touchController.postEvent(
                    MOUSE_REQUIRE,
                    -1,
                    self.realtiveX,
                    self.realtiveY,
                )
                # 重新计算映射坐标
                self.realtiveX -= y
                self.realtiveY -= x
            # print("MOUSE MOVE [",self.realtiveX,self.realtiveY,"]")
            # 鼠标移动
            self.touchController.postEvent(
                MOVE_FLAG, self.mouseTouchID, self.realtiveX, self.realtiveY
            )
        elif type == RELEASE_FLAG:
            self.touchController.postEvent(RELEASE_FLAG, self.mouseTouchID, 0, 0)
            self.mouseTouchID = -1
        self.mouseLock.release()

    def handelKeyAction(self, keycode, updown):
        action = self.keyMap[keycode]
        if action["TYPE"] == "PRESS":  # 按下 发送按下事件 松开 发送松开事件
            if updown == DOWN:
                self.keyMappingDatas[keycode] = self.touchController.postEvent(
                    REQURIE_FLAG,
                    -1,
                    action["POS"][0] + getRand(),
                    action["POS"][1] + getRand(),
                )
            else:
                self.touchController.postEvent(
                    RELEASE_FLAG, self.keyMappingDatas[keycode], -1, -1
                )

        elif action["TYPE"] == "CLICK":  # 仅响应按下 触发一次点击事件 间隔
            if updown == DOWN:
                self.keyMappingDatas[keycode] = self.touchController.postEvent(
                    REQURIE_FLAG,
                    -1,
                    action["POS"][0] + getRand(),
                    action["POS"][1] + getRand(),
                )
                time.sleep(action["INTERVAL"][0] / 1000)
                self.touchController.postEvent(
                    RELEASE_FLAG, self.keyMappingDatas[keycode], -1, -1
                )

        elif action["TYPE"] == "AUTO_FIRE":  # 按下时触发 松开停止 自动连续点击，点击时长与间隔可调
            if updown == DOWN:
                self.keyMappingDatas[keycode] = True
                while self.keyMappingDatas[keycode]:
                    touch_id = self.touchController.postEvent(
                        REQURIE_FLAG,
                        -1,
                        action["POS"][0] + getRand(),
                        action["POS"][1] + getRand(),
                    )
                    time.sleep(action["INTERVAL"][0] / 1000)
                    self.touchController.postEvent(RELEASE_FLAG, touch_id, -1, -1)
                    time.sleep(action["INTERVAL"][1] / 1000)
            else:
                self.keyMappingDatas[keycode] = False

        elif action["TYPE"] == "DRAG":  # 仅响应按下 触发一次拖动事件 间隔可调
            if keycode not in self.keyMappingDatas:
                self.keyMappingDatas[keycode] = -1
            if updown == DOWN and self.keyMappingDatas[keycode] == -1:
                # down p0 sleep p1 sleep p2 sleep ...... pn-1 sleep  pn release
                self.keyMappingDatas[keycode] = self.touchController.postEvent(
                    REQURIE_FLAG, -1, action["POS_S"][0][0], action["POS_S"][0][1]
                )
                for pos in action["POS_S"][1:]:
                    time.sleep(action["INTERVAL"][0] / 1000)
                    self.touchController.postEvent(
                        MOVE_FLAG,
                        self.keyMappingDatas[keycode],
                        pos[0],
                        pos[1],
                    )
                self.touchController.postEvent(
                    RELEASE_FLAG, self.keyMappingDatas[keycode], -1, -1
                )
                self.keyMappingDatas[keycode] = -1

        elif action["TYPE"] == "MULT_PRESS":  # 按下时触发 松开停止  按顺序点击多个位置 松开时反顺序松开
            if updown == DOWN:
                self.keyMappingDatas[keycode] = []
                for [pos_x, pos_y] in action["POS_S"]:
                    self.keyMappingDatas[keycode].append(
                        self.touchController.postEvent(
                            REQURIE_FLAG,
                            -1,
                            pos_x + getRand(),
                            pos_y + getRand(),
                        )
                    )
            else:
                for touch_id in reversed(self.keyMappingDatas[keycode]):
                    self.touchController.postEvent(RELEASE_FLAG, touch_id, -1, -1)

    def printInfo(self):
        print(json.dumps(self.keyMap, indent=4))
        print(json.dumps(self.wheelMap, indent=4))

    def changeWheelStause(self, key, updown):
        # 更新wasd按键的状态 并根据状态计算新坐标
        self.wheel_satuse[self.wheel_wasd.index(key)] = updown
        x_Asix = 1 - self.wheel_satuse[1] + self.wheel_satuse[3]
        y_Asix = 1 - self.wheel_satuse[2] + self.wheel_satuse[0]
        map_value = x_Asix * 3 + y_Asix
        self.wheelTarget = self.wheelMap[map_value]

    def handelEvents(self, events):
        # 全局变量 是否是映射模式
        global global_exclusive_flag, InterruptedFlag
        # x,y 鼠标坐标
        x, y = 0, 0
        for (type, code, value) in events:
            # 如果是模式切换键释放 则切换模式
            if type == EV_KEY and code == self.SWITCH_KEY:
                if value == UP:
                    self.switch_key_down = False
                    global_exclusive_flag = not global_exclusive_flag
                    print("exclusive mode:", global_exclusive_flag)
                    return
                else:
                    self.switch_key_down = True
                    return

            # 非独占模式 且 switch按下中 按下esc键 则退出
            if (
                self.switch_key_down
                and global_exclusive_flag == False
                and type == EV_KEY
                and code == 1
                and value == UP
            ):
                global_exclusive_flag = not global_exclusive_flag
                InterruptedFlag = True
                print("SWITCH_KEY + ESC pressed ,now exit ...")
                return

            # 当处于映射模式时 处理事件
            if global_exclusive_flag == True:
                # 如果是坐标事件 则修改x,y坐标 并在全部事件处理完成后再处理
                if type == EV_REL:
                    x = value if code == REL_X else x
                    y = value if code == REL_Y else y
                # 如果是按键事件 则立即处理
                elif type == EV_KEY:
                    # 如果是方向键 则改变滚轮状态 使用changeWheelStause处理
                    if code in self.wheel_wasd:
                        self.changeWheelStause(code, value)
                    # 如果在映射表中找到了对应的按键 则开一个线程去处理
                    elif code in self.keyMap:
                        threading.Thread(
                            target=self.handelKeyAction,
                            args=(code, value),
                        ).start()
                    # 按键不在映射表中 则输出按键信息
                    else:
                        print("KEY_CODE = ", code, " not in keyMap")

        # 如果处于映射模式且x或y坐标不为0  在这里处理鼠标事件
        if global_exclusive_flag == True and (x != 0 or y != 0):
            self.handelMouseMoveAction(offsetX=x, offsetY=y)

    def handelJSBTNAction(self, key, updown):
        if key == "BTN_SELECT":
            self.js_switch_key_down = updown
        
        if self.js_switch_key_down == DOWN and key == "BTN_RS":
            print("switch mode")
        
        if key in self.keyMap:
            threading.Thread(
                target=self.handelKeyAction,
                args=(key, updown),
            ).start()
        # 按键不在映射表中 则输出按键信息
        else:
            print("KEY_CODE = ", key, " not in keyMap")

    def handelABSAction(self, name, value):
        if name in LR_RT_VALUEMAP:
            for (keyPoint, keyName) in LR_RT_VALUEMAP[name]:
                if self.abs_last[name] < keyPoint and value >= keyPoint:
                    updown = DOWN
                    self.handelJSBTNAction(keyName, updown)
                elif self.abs_last[name] >= keyPoint and value < keyPoint:
                    updown = UP
                    self.handelJSBTNAction(keyName, updown)
                else:
                    pass
            self.abs_last[name] = value
        elif name == "HAT0X" or name == "HAT0Y":
            direction, updown = HAT_D_U[
                "{:.1f}_{:.1f}".format(self.abs_last[name], value)
            ]
            keyName = HAT0_KEYNAME[name][direction]
            self.abs_last[name] = value
            self.handelJSBTNAction(keyName, updown)
        else:
            assert name in ["LS_X", "LS_Y", "RS_X", "RS_Y"]
            if name in ["LS_X", "LS_Y"]:
                self.abs_last[name] = value
                ls_dz = self.jsInfo["DEADZONE"]["LS"]
                if (
                    ls_dz[0] < (self.abs_last["LS_X"]) < ls_dz[1]
                    and ls_dz[0] < (self.abs_last["LS_Y"]) < ls_dz[1]
                ):
                    self.handelWheelMoveAction(type=RELEASE_FLAG)  # 释放过则两个判断后直接返回
                else:
                    wheelX = self.wheelMap[4][0] + self.wheel_range * 2 * (
                        self.abs_last["LS_X"] - 0.5
                    )
                    wheelY = self.wheelMap[4][1] + self.wheel_range * 2 * (
                        self.abs_last["LS_Y"] - 0.5
                    )
                    self.handelWheelMoveAction(targetX=int(wheelY), targetY=int(wheelX))
            elif name in ["RS_X", "RS_Y"]:
                self.abs_last[name] = value
                rs_dz = self.jsInfo["DEADZONE"]["RS"]
                if (
                    rs_dz[0] < (self.abs_last["RS_X"]) < rs_dz[1]
                    and rs_dz[0] < (self.abs_last["RS_Y"]) < rs_dz[1]
                ):
                    self.abs_last[name] = 0.5

    def handelJSEvents(self, events):
        for (type, code, value) in events:
            if type == EV_ABS:
                name = self.jsInfo["ABS"][code]["name"]
                minVal, maxVal = self.jsInfo["ABS"][code]["range"]
                direction = self.jsInfo["ABS"][code]["reverse"]
                formatedValue = (value - minVal) / (maxVal - minVal)
                formatedValue = 1 - formatedValue if direction else formatedValue
                self.handelABSAction(name, formatedValue)
            elif type == EV_KEY:
                if code in self.jsInfo["BTN"]:
                    name = self.jsInfo["BTN"][code]["name"]
                    self.handelJSBTNAction(name, value)
                # else:
                #     # print("BTN", code, "not in BTN")
                #     pass


def noexclusiveMode(keyboardEvenPath, handelerInstance):
    global global_exclusive_flag
    print("非独占模式")
    buffer = []
    with open(keyboardEvenPath, "rb") as f:
        while not global_exclusive_flag:
            byte = f.read(EVENT_SIZE)
            e_sec, e_usec, e_type, e_code, e_val = struct.unpack(EVENT_FORMAT, byte)
            # print(e_type, e_code, e_val)
            if e_type == 0 and e_code == 0 and e_val == 0:
                handelerInstance.handelEvents(buffer)
                buffer.clear()
            else:
                buffer.append(
                    (
                        e_type,
                        e_code,
                        e_val if e_val <= 0x7FFFFFFF else e_val - 0x100000000,
                    )
                )
            # handelerInstance.handelEvent(e_type, e_code, e_val)
    print("退出 非独占模式")


def exclusiveMode(keyboardEvenPath, mouseEventPath, handelerInstance):
    global global_exclusive_flag
    print("独占模式")

    def readMouseEvent():
        buffer = []
        with open(mouseEventPath, "rb") as f:
            fcntl.ioctl(f, EVIOCGRAB(1), True)
            while global_exclusive_flag:
                byte = f.read(EVENT_SIZE)
                e_sec, e_usec, e_type, e_code, e_val = struct.unpack(EVENT_FORMAT, byte)

                if e_type == 0 and e_code == 0 and e_val == 0:
                    handelerInstance.handelEvents(buffer)
                    buffer.clear()
                else:
                    buffer.append(
                        (
                            e_type,
                            e_code,
                            e_val if e_val <= 0x7FFFFFFF else e_val - 0x100000000,
                        )
                    )

                # handelerInstance.handelEvent(e_type, e_code, e_val)

    def readKeyboardEvent():
        buffer = []
        with open(keyboardEvenPath, "rb") as f:
            fcntl.ioctl(f, EVIOCGRAB(1), True)
            while global_exclusive_flag:
                byte = f.read(EVENT_SIZE)
                e_sec, e_usec, e_type, e_code, e_val = struct.unpack(EVENT_FORMAT, byte)

                if e_type == 0 and e_code == 0 and e_val == 0:
                    handelerInstance.handelEvents(buffer)
                    buffer.clear()
                else:
                    buffer.append(
                        (
                            e_type,
                            e_code,
                            e_val if e_val <= 0x7FFFFFFF else e_val - 0x100000000,
                        )
                    )

                # handelerInstance.handelEvent(e_type, e_code, e_val)

    mouseReadingThread = threading.Thread(target=readMouseEvent)
    keyboardReadingThread = threading.Thread(target=readKeyboardEvent)

    mouseReadingThread.start()
    keyboardReadingThread.start()

    mouseReadingThread.join()
    keyboardReadingThread.join()

    print("退出 独占模式")


def jsnoexclusiveMode(jsEvenPath, handelerInstance):
    global global_exclusive_flag
    print("非独占模式")
    buffer = []
    with open(jsEvenPath, "rb") as f:
        while not global_exclusive_flag:
            byte = f.read(EVENT_SIZE)
            e_sec, e_usec, e_type, e_code, e_val = struct.unpack(EVENT_FORMAT, byte)
            # print(e_type, e_code, e_val)
            if e_type == 0 and e_code == 0 and e_val == 0:
                handelerInstance.handelJSEvents(buffer)
                buffer.clear()
            else:
                buffer.append(
                    (
                        e_type,
                        e_code,
                        e_val if e_val <= 0x7FFFFFFF else e_val - 0x100000000,
                    )
                )
            # handelerInstance.handelEvent(e_type, e_code, e_val)
    print("退出 非独占模式")


InterruptedFlag = False

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("args error!")
        exit()

    if sys.argv[1] == "js":  # 这种方式只是暂时的 最终实现的是所有设备都可以同时使用
        touchEventPath = "/dev/input/event{}".format(sys.argv[2])
        jsEventPath = "/dev/input/event{}".format(sys.argv[3])
        configFilPath = sys.argv[4]
        if not os.path.exists(configFilPath):
            print("config file error!")
            exit()
        map_config = json.load(open(configFilPath, "r", encoding="UTF-8"))

        # 0 : LS 左->右 0 -> 255
        # 1 : LS 上->下 0-> 255
        # 2 : RS 左->右 0 -> 255
        # 5 : RS 上->下 0->255
        # 3 : LT 0->255
        # 4 : RT 0->255
        ds5Config = {
            "DEADZONE": {
                "LS": [0.5 - 0.08, 0.5 + 0.08],
                "RS": [0.5 - 0.015, 0.5 + 0.015],
            },
            "ABS": {
                0: {
                    "name": "LS_X",
                    "range": [0, 255],
                    "reverse": False,
                },
                1: {
                    "name": "LS_Y",
                    "range": [0, 255],
                    "reverse": True,
                },
                2: {
                    "name": "RS_X",
                    "range": [0, 255],
                    "reverse": False,
                },
                5: {
                    "name": "RS_Y",
                    "range": [0, 255],
                    "reverse": False,
                },
                3: {
                    "name": "LT",
                    "range": [0, 255],
                    "reverse": False,
                },
                4: {
                    "name": "RT",
                    "range": [0, 255],
                    "reverse": False,
                },
                16: {
                    "name": "HAT0X",
                    "range": [-1, 1],
                    "reverse": False,
                },
                17: {
                    "name": "HAT0Y",
                    "range": [-1, 1],
                    "reverse": False,
                },
            },
            "BTN": {
                305: {"name": "BTN_A"},
                306: {"name": "BTN_B"},
                304: {"name": "BTN_X"},
                307: {"name": "BTN_Y"},
                312: {"name": "BTN_SELECT"},
                313: {"name": "BTN_START"},
                316: {"name": "BTN_HOME"},
                308: {"name": "BTN_LB"},
                309: {"name": "BTN_RB"},
                314: {"name": "BTN_LS"},
                315: {"name": "BTN_RS"},
                317: {"name": "BTN_THUMBL"},
            },
        }

        touchControlInstance = touchController(touchEventPath)
        handelerInstance = eventHandeler(
            map_config, touchControlInstance, jsInfo=ds5Config
        )
        jsnoexclusiveMode(jsEventPath, handelerInstance)

    else:
        touchEventPath = "/dev/input/event{}".format(sys.argv[1])
        mouseEventPath = "/dev/input/event{}".format(sys.argv[2])
        keyboardEvenPath = "/dev/input/event{}".format(sys.argv[3])
        configFilPath = sys.argv[4]

        if not os.path.exists(configFilPath):
            print("config file error!")
            exit()

        map_config = json.load(open(configFilPath, "r", encoding="UTF-8"))

        touchControlInstance = touchController(touchEventPath)
        handelerInstance = eventHandeler(map_config, touchControlInstance)

        while True:
            noexclusiveMode(keyboardEvenPath, handelerInstance)
            if InterruptedFlag == True:
                handelerInstance.destroy()
                exit(0)
            exclusiveMode(keyboardEvenPath, mouseEventPath, handelerInstance)
