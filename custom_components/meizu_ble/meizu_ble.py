import paho.mqtt.client as mqtt
import json, time, hashlib, threading, random
from shaonianzhentan import load_yaml
from meizu import MZBtIr

def md5(text):
    data = hashlib.md5(text.encode('utf-8')).hexdigest()
    return data[8:-8]

# 读取配置
config = load_yaml('meizu_ble.yaml')
config_mqtt = config['mqtt']
client_id = "meizu_ble"
HOST = config_mqtt['host']
PORT = int(config_mqtt['port'])
USERNAME = config_mqtt['user']
PASSWORD = config_mqtt['password']
SCAN_INTERVAL = config.get('scan_interval', 300)
# 自动发现
discovery_topic = "homeassistant/status"
# 读取红外码
config_ir = load_yaml('ir.yaml')

# 自动配置
def auto_config(domain, data, mac):
    param = {
        "device":{
            "name": "魅族智能遥控器",
            "identifiers": [ mac ],
            "model": mac,
            "sw_version": "1.0",
            "manufacturer":"shaonianzhentan"
        },
    }
    param.update(data)
    client.publish(f"homeassistant/{domain}/{data['unique_id']}/config", payload=json.dumps(param), qos=0)

# 自动发送信息
def auto_publish():
    for config_meizu in config['meizu']:
        mac = config_meizu['mac']
        # 获取设备信息
        # print(mac)
        try:
            ble = MZBtIr(mac)
            ble.update()
            temperature = ble.temperature()
            humidity = ble.humidity()
            voltage = ble.voltage()
            battery = ble.battery()
            # 为 0 则不上报，防止异常数据
            if temperature != 0:
                client.publish(f"meizu_ble/{mac}/temperature", payload=temperature, qos=0)
            if humidity != 0:
                client.publish(f"meizu_ble/{mac}/humidity", payload=humidity, qos=0)
            # 如果电量大于0，则推送，否则会有异常信息
            if battery > 0:                
                client.publish(f"meizu_ble/{mac}/battery", payload=battery, qos=0)
                attrs = {
                    'voltage': voltage,
                    'mac': mac
                }
                client.publish(f"meizu_ble/{mac}/battery/attrs", payload=json.dumps(attrs), qos=0)
            time.sleep(2)
        except Exception as ex:
            print(f"{mac}：出现异常")
            print(ex)

    global timer
    timer = threading.Timer(SCAN_INTERVAL, auto_publish)
    timer.start()

# 自动发现配置
def discovery_config():
    options = []
    for key in config_ir:
        for ir_key in config_ir[key]:
            options.append(f"{key}_{ir_key}")

    # 读取配置
    for config_meizu in config['meizu']:
        name = config_meizu['name']
        mac = config_meizu['mac']

        select_unique_id = md5(f"{mac}红外遥控")
        command_topic = f"meizu_ble/{select_unique_id}/{mac}"
        client.subscribe(command_topic)
        # 自动配置红外遥控
        auto_config("select", {
            "unique_id": select_unique_id,
            "name": f"{name}红外遥控",
            "state_topic": f"meizu_ble/{mac}/irdata",
            "command_topic": command_topic,
            "options": options
        }, mac)
        # 自动配置温湿度传感器
        auto_config("sensor", {
            "unique_id": md5(f"{mac}温度"),
            "name": f"{name}温度",
            "state_topic": f"meizu_ble/{mac}/temperature",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
        }, mac)
        auto_config("sensor", {
            "unique_id": md5(f"{mac}湿度"),
            "name": f"{name}湿度",
            "state_topic": f"meizu_ble/{mac}/humidity",
            "unit_of_measurement": "%",
            "device_class": "humidity"
        }, mac)
        auto_config("sensor", {
            "unique_id": md5(f"{mac}电量"),
            "name": f"{name}电量",
            "state_topic": f"meizu_ble/{mac}/battery",
            "json_attributes_topic": f"meizu_ble/{mac}/battery/attrs",
            "unit_of_measurement": "%",
            "device_class": "battery"
        }, mac)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(discovery_topic)
    discovery_config()
    # 定时执行获取设备信息
    timer = threading.Timer(10, auto_publish)
    timer.start()

# 发送红外命令
ir_counter = 0
def send_irdata(mac, ir_command):
    global ir_counter
    try:
        ble = MZBtIr(mac)
        ble.sendIrRaw(ir_command)
        print('红外命令发送成功')
        ir_counter = 0
    except Exception as ex:
        print(f"{mac}：出现异常，正在重试: {ir_counter}")
        print(ex)
        # 出现异常，进行重试
        if ir_counter < 2:
            ir_counter = ir_counter + 1
            send_irdata(mac, ir_command)


def on_message(client, userdata, msg):
    payload = str(msg.payload.decode('utf-8'))
    print("主题:" + msg.topic + " 消息:" + payload)
    # 自动发现配置
    if msg.topic == discovery_topic and payload == 'online':
        discovery_config()
        return
    # 发送红外命令
    arr = msg.topic.split('/')
    mac = arr[len(arr)-1]
    arr = payload.split('_', 1)
    if len(arr) == 2:
        device = arr[0]
        command = arr[1]
        print(mac, device, command)
        if device in config_ir:
            if command in config_ir[device]:
                print('发送红外命令')
                ir_command = config_ir[device][command]
                send_irdata(mac, ir_command)
                # 重置数据
                client.publish(f"meizu_ble/{mac}/irdata", payload='', qos=0)

def on_subscribe(client, userdata, mid, granted_qos):
    print("On Subscribed: qos = %d" % granted_qos)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection %s" % rc)
        global timer
        timer.cancel()

client = mqtt.Client(client_id)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect
client.connect(HOST, PORT, 60)
client.loop_forever()