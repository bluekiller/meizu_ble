# 魅族蓝牙红外遥控温湿度传感器

注意：只在树莓派之中测试过

本插件是基于原作者的研究进行套壳接入HA，关于设备的整体操作与获取，请参考原作者代码

原项目地址：https://github.com/junnikokuki/Meizu-BLE-Thermometer

---

- [蓝牙抓包，红外码解析 点这里](./meizu_ir_reader_from_android/)
- [遥控红外码，支持部分内置设备 点这里](./remote/)

## 配置

```yaml
# 基础配置
sensor:
  - platform: meizu_ble
    mac: '68:3E:34:CC:E0:67'

# 完整配置
sensor:
  - platform: meizu_ble
    name: 魅族智能遥控器
    mac: '68:3E:34:CC:E0:67'
    scan_interval: 60

# 遥控器（请大家多多贡献自己录的码）
remote:
  - platform: meizu_ble
    name: 魅族智能遥控器  
    mac: '68:3E:34:CC:E0:67'
```

> 分组

```yaml
group:
  meizu_ble_1:
    name: 魅族智能遥控器
    entities:
      - sensor.mei_zu_zhi_neng_yao_kong_qi_wen_du
      - sensor.mei_zu_zhi_neng_yao_kong_qi_shi_du
      - sensor.mei_zu_zhi_neng_yao_kong_qi_dian_liang
  meizu_ble_2:
    name: 魅族智能遥控器
    entities:
      - sensor.mei_zu_zhi_neng_yao_kong_qi_wen_du
      - sensor.mei_zu_zhi_neng_yao_kong_qi_shi_du
      - sensor.mei_zu_zhi_neng_yao_kong_qi_dian_liang
```

## 更新日志

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