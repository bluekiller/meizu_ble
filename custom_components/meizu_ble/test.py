from meizu import MZBtIr

ble = MZBtIr('68:3E:34:CC:E0:67')

ir = '5c001cc8d94613bb5a:55005c200022000001becf651db7cbdd1d0bcfdf2560f3e120d2fff62d24fbf02d26fff22528f3fc252aeffe3d2cebf83d2eeffa2530f3e42532ffe62d34fbe02d36ffe22538f3ec253acecc3c2ddaca3c2fddcb7751a28644609ccf'
arr = ir.split(':')
ble.sendIr(arr[0], arr[1])