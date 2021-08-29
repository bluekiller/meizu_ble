#from meizu import MZBtIr

#ble = MZBtIr('68:3E:34:CC:E0:67')

#print('开始录码')
#print(ble.receiveIr())
# ble.sendIr("5c001cc8d94613bb5a", "55005c200022000001becf651db7cbdd1d0bcfdf2560f3e120d2fff62d24fbf02d26fff22528f3fc252aeffe3d2cebf83d2eeffa2530f3e42532ffe62d34fbe02d36ffe22538f3ec253acecc3c2ddaca3c2fddcb7751a28644609ccf")


# [98, 6, 24, 1, 65, 1, 1, 2, 1, 1, 1, 0, 170, 5, 110, 0, 21, 0, 163, 0, 21, 2, 1, 0, 7, 2, 116, 0, 3, 1, 56, 0, 1, 255, 255, 254]

def handleNotification(data):
    _received_packet = 0
    _receive_buffer = []
    _total_packet = 0
    if len(data) > 4 and data[3] == 9:
        if data[4] == 0:
            _total_packet = data[5]
            _receive_buffer = []
            _received_packet = _received_packet + 1
        elif data[4] == _received_packet:
            _receive_buffer.extend(data[5:])
            _received_packet = _received_packet + 1
        else:
            _receive_buffer = False
            _total_packet = -1
    print(_received_packet)
    print(_total_packet)
    print(_receive_buffer)


bb = bytes([98, 6, 24, 1, 65, 1, 1, 2, 1, 1, 1, 0, 170, 5, 110, 0, 21, 0, 163, 0, 21, 2, 1, 0, 7, 2, 116, 0, 3, 1, 56, 0, 1, 255, 255, 254])
print(bb.hex())
