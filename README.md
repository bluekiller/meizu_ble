# 魅族蓝牙红外遥控温湿度传感器

注意：只在树莓派之中测试过

本插件是基于原作者的研究进行套壳接入HA，关于设备的整体操作与获取，请参考原作者代码

原项目地址：https://github.com/junnikokuki/Meizu-BLE-Thermometer


> 配置

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
    scan_interval: 30


# 遥控器（请大家多多贡献自己录的码）
remote:
  - platform: meizu_ble
    name: 魅族智能遥控器  
    mac: '68:3E:34:CC:E0:67'
```

> 遥控器使用说明（由于录码比较繁琐，建议大家贡献自己录的码，然后集成到插件之中使用）

下面是大家贡献的设备与命令，通过调用 `remote.send_command` 服务传入设备与命令即可

```yaml
海信HZ65U7E:
  power: 开关机
  up: 上
  down: 下
  left: 左
  right: 右
  source: 信号来源
  enter: 确认
  back: 返回
  menu: 菜单
  volumedown: 音量减小
  volumeup: 音量增加
  mute: 静音
  sleep: 休眠
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

> 已知问题

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

   