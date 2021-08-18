# 魅族蓝牙红外遥控温湿度传感器

注意：只在树莓派之中测试过

本插件是基于原作者的研究进行套壳接入HA，关于设备的整体操作与获取，请参考原作者代码

原项目地址：https://github.com/junnikokuki/Meizu-BLE-Thermometer


> 配置

```yaml
sensor:
  - platform: meizu_ble
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