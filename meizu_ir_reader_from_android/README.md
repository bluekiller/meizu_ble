# Android手机蓝牙抓包

请先参考原项目：https://github.com/junnikokuki/Meizu-BLE-Thermometer/tree/master/meizu_ir_reader_from_android

本项目采用直接读取文件的方式

1. 将`btsnoop_hci.log`放到当前目录，与`irdatareader.py`同级
1. 执行`python3 irdatareader.py`命令
1. 显示结果红外码结果，结束

注意：不知道是我的手机蓝牙抓包问题，还是程序解析的问题，只能解析最后一个红外码