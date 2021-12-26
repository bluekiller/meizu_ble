# 魅族蓝牙红外遥控温湿度传感器

[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

![visit](https://visitor-badge.glitch.me/badge?page_id=shaonianzhentan.meizu_ble&left_text=visit)
![forks](https://img.shields.io/github/forks/shaonianzhentan/meizu_ble)
![stars](https://img.shields.io/github/stars/shaonianzhentan/meizu_ble)

## 安装方式

安装完成重启HA，刷新一下页面，在集成里搜索`魅族智能遥控器`即可

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=meizu_ble)

注意：只在树莓派之中测试过

本插件是基于原作者的研究进行套壳接入HA，关于设备的整体操作与获取，请参考原作者代码

原项目地址：https://github.com/junnikokuki/Meizu-BLE-Thermometer

---

- [蓝牙抓包，红外码解析 点这里](./meizu_ir_reader_from_android/)
- [遥控红外码，支持部分内置设备 点这里](./remote/)

## 更新日志

- 更新时间默认5分钟
- 增加小米电视开关红外码
- 增加乐视超级电视红外码

## 已知问题

树莓派的蓝牙有点辣鸡，可能会有获取失败的情况发生，这个时候一般重启蓝牙就好了

```bash
# 关闭蓝牙
sudo hciconfig hci0 down

# 打开蓝牙
sudo hciconfig hci0 up

# 如果报下面这个异常的话，就执行下面的命令
# Can't init device hci0: Connection timed out (110)

rfkill block bluetooth

rfkill unblock bluetooth

sudo hciconfig hci0 up

# 一般重启蓝牙后，过30秒就会显示信息了
# 如果还是不行的话，那对不起，告辞，再见
```

---

在非树莓派的环境之中，有些设备有蓝牙模块，但因为版本型号的关系，可能无法在docker内部编译`bluepy`这个依赖
如果在系统之中可以编译这个依赖，可以使用MQTT方式接入

```bash
# 安装相关依赖
pip3 install bluepy paho-mqtt pyyaml

# 修改 meizu_ble.yaml 配置文件

# 运行主程序
python3 meizu_ble.py


```

```bash
# 如果有安装NodeJs环境，可以使用pm2开机启动管理
pm2 start meizu_ble.py -x --interpreter python3

# 重启
pm2 restart meizu_ble

# 查看日志
pm2 logs meizu_ble

```