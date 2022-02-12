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
sudo python ./main.py 触屏设备号 鼠标设备号 键盘设备号 映射文件路径
```



[创建映射文件](https://driverlin.github.io/py-touch-mapper/create-mapper/build/)

按住键盘按键点击即可添加映射

8 9 0 分别对应鼠标 左 中 右 键 

如有需要 可手动新修改配置文件