# Exclusive_mode_mapper
## 说明
[mouse-keyboard-map-touch](https://github.com/DriverLin/mouse-keyboard-map-touch)的python实现

相比于C的版本，扩展功能的开发更加方便


## 使用方法
查看自己的触屏鼠标和键盘对应的设备号。
```
sudo getevent -l
```

下载
```
git clone https://github.com/DriverLin/py-touch-mapper
```

执行
```
cd py-touch-mapper
sudo python ./main.py 触屏设备号 鼠标设备号 键盘设备号 手柄设备号 映射文件路径
```

如果没有启用某个设备 设备号输入一个小于等于0的值

例如在仅启用手柄的情况下

```
sudo python ./main.py 触屏设备号 0 0 手柄设备号 映射文件路径
```

切换映射开关

默认键盘使用 ` 键，可在配置文件中修改，手柄为SELECT+RS组合键


## 触屏映射文件
[创建映射文件工具](https://driverlin.github.io/py-touch-mapper/create-mapper/build/)

按住键盘按键点击即可添加映射

8 9 0 分别对应鼠标 左 中 右 键 

如有需要，可参照[EXAMPLE.JSON](https://github.com/DriverLin/py-touch-mapper/blob/main/EXAMPLE.JSON)手动修改配置文件


## 关于手柄

手柄为模拟键鼠和映射触屏两种模式

模拟键鼠时，左摇杆为滚轮，右摇杆为鼠标

其他按键映射可在映射配置文件中设置

映射触屏时，左摇杆为移动摇杆，右摇杆控制视角


## 手柄配置文件

在[joystickInfos](https://github.com/DriverLin/py-touch-mapper/tree/main/joystickInfos)中内置了常见手柄的配置文件 

可使用 
```
sudo python ./create_joystick_config.py 手柄设备号  
```
创建手柄配置文件

手柄按照按键位置统一格式化为XBOX手柄布局， 因此触屏映射配置文件是通用的

扳机键按照力度映射为5个等级的按键 例如 BTN_LT_1 BTN_LT_2 ... BTN_LT_5

没有线性扳机的手柄例如 Switch Pro controller 只有 BTN_LT 和 BTN_RT