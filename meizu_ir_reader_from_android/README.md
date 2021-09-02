# Android手机蓝牙抓包

请先参考原项目：https://github.com/junnikokuki/Meizu-BLE-Thermometer/tree/master/meizu_ir_reader_from_android

## 关于Android设备获取蓝牙调试日志 `btsnoop_hci.log` 的方法

由于原项目已经过去了2年之久，部分操作方法可能已经不适用于现在的Android设备了，如果使用原项目的操作方式不行的话，可以试试以下操作方式

> 小米手机抓取蓝牙日志（使用MI 9 测试正常）
1. 打开开发者选项，打开蓝牙调试日志和蓝牙数据包日志开关
1. 在拨号盘输入一次  `*#*#5959#*#*`  即开始抓蓝牙日志
1. 在魅家添加需要获取遥控码的设备，并把需要获取的按键按顺序按一遍（记住顺序）
1. 再拨号盘输入一次  `*#*#5959#*#*`
1. 等待大概半分钟，在文件管理器中 `/sdcard/MIUI/debug_log`下会生成`bugreport-当前时间.zip`调试文件
1. 解压调试文件，然后找到解压目录中的文件 `common/com.android.bluetooth/btsnoop_hci.log`
1. 将本项目clone到本地
1. 将`btsnoop_hci.log`放到当前目录，与`irdatareader.py`同级
1. 然后执行`python3 irdatareader.py`
1. 如果没啥毛病，就会显示红外码了


注意：不知道是我的手机蓝牙抓包问题，还是程序解析的问题，只能解析最后一个红外码，有的手机解析正常