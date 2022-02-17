# 安卓触屏映射工具
## 说明
[mouse-keyboard-map-touch](https://github.com/DriverLin/mouse-keyboard-map-touch)的python实现

相比于C的版本，扩展功能的开发更加方便


## 使用方法

下载
```
git clone https://github.com/DriverLin/py-touch-mapper
```
查看自己的触屏鼠标和键盘对应的设备号。
```
sudo getevent -l
```
执行
```
cd py-touch-mapper

sudo python ./main.py -h

usage: main.py [-h] [-t int] [-n int [int ...]] [-m int [int ...]]
               [-k int [int ...]] [-j int [int ...]] [-c str] [-u [bool]] [-p int]
               [-r [bool]] [-a str]

options:
  -h, --help            show this help message and exit
  -t int, --touch int   touch event index 触屏设备号
  -n int [int ...], --normal int [int ...]
                        mouse or keyboard event index 鼠标或键盘设备号
  -m int [int ...], --mouse int [int ...]
                        mouse event index 鼠标设备号
  -k int [int ...], --keyboard int [int ...]
                        keyboard event index 键盘设备号
  -j int [int ...], --joystick int [int ...]
                        joystick event index 手柄设备号
  -c str, --mapconfig str
                        map config file 触屏映射文件
  -u [bool], --udp [bool]
                        recv remote events through udp 是否通过udp接受远程事件
  -p int, --port int    udp listen port 远程事件接收端口号
  -r [bool], --remote [bool]
                        remote mode ,send local events to remote 远程模式,发送所有本地事件到远程
  -a str, --addr str    remote ip 远程设备ip端口号

```
## 示例

```
触屏 /dev/input/event5
鼠标1 /dev/input/event15
鼠标2 /dev/input/event19
键盘 /dev/input/event16
手柄 /dev/input/event17
配置文件 pubg.json 
```
启用鼠标1 鼠标2 键盘 手柄
```
sudo python main.py -t 5 -n 15 16 19 -j 17 -c pubg.json  
```
仅启用鼠标1与手柄
```
sudo python main.py -t 5 -n 15 -j 17 -c pubg.json  
```
事件发送模式
```
sudo python main.py -n 15 16 -j 17 -r -a 127.0.0.1:9000 
```
在端口9000接收远程事件
```
sudo python main.py -t 5 -n 15 16 19 -j 17 -c pubg.json   -u -p 9000
```

## 切换映射模式
默认键盘使用 ` 键，可在配置文件中修改，手柄为SELECT+RS组合键


## 触屏映射文件
[创建映射文件工具](https://driverlin.github.io/py-touch-mapper/build/)

按住键盘按键点击即可添加映射

8 9 0 分别对应鼠标 左 中 右 键 

如有需要，可参照[EXAMPLE.JSON](https://github.com/DriverLin/py-touch-mapper/blob/main/EXAMPLE.JSON)手动修改配置文件


## 关于手柄

手柄为模拟键鼠和映射触屏两种模式

模拟键鼠时，左摇杆为滚轮，右摇杆为鼠标

其他按键映射可在映射配置文件中设置

映射触屏时，左摇杆为移动摇杆，右摇杆控制视角


## 手柄配置文件
手柄按照按键位置统一格式化为XBOX手柄布局， 因此触屏映射配置文件是通用的

扳机键按照力度映射为5个等级的按键 例如 BTN_LT_1 BTN_LT_2 ... BTN_LT_5

没有线性扳机的手柄例如 Switch Pro controller 只有 BTN_LT 和 BTN_RT

在[joystickInfos](https://github.com/DriverLin/py-touch-mapper/tree/main/joystickInfos)中内置了常见手柄的配置文件 

可使用 
```
sudo python ./create_joystick_config.py 手柄设备号  
```
创建手柄配置文件

