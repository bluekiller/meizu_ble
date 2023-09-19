import logging
from binascii import a2b_hex
from threading import Lock

from bleak import BleakClient, BLEDevice

SERVICE_UUID = "000016f2-0000-1000-8000-00805f9b34fb"
_LOGGER = logging.getLogger(__name__)


class MZBtIr(object):

    def __init__(self, ble_device: BLEDevice):
        """
        Initialize a Meizu for the given MAC address.
        """
        self._lock = Lock()
        self._sequence = 0
        self._temperature = None
        self._humidity = None
        self._battery = None
        self._receive_handle = None
        self._receive_buffer = None
        self._received_packet = 0
        self._total_packet = -1
        self._ble_device = ble_device
        self._client = None

    async def close(self):
        if self._client and self._client.is_connected:
            await self._client.disconnect()
            self._client = None

    async def _ensure_connected(self):
        if self._client is None:
            _LOGGER.debug('creating client')
            self._client = BleakClient(self._ble_device)
        if self._client.is_connected:
            _LOGGER.debug('client is already connected')
            return
        _LOGGER.debug('try to connect')
        await self._client.connect()

    def get_sequence(self):
        self._sequence += 1
        if self._sequence > 255:
            self._sequence = 0
        return self._sequence

    def mac(self):
        return self._ble_device.address

    def temperature(self):
        return self._temperature

    def humidity(self):
        return self._humidity

    def battery(self):
        if self.voltage() is None:
            return None

        v = self.voltage()
        b = int((v - 2.3) / 0.7 * 100)
        if b < 0:
            b = 0
        return b

    def voltage(self):
        return self._battery

    async def update(self, update_battery=True):
        self._lock.acquire()
        try:
            await self._ensure_connected()
            await self._client.write_gatt_char(SERVICE_UUID,
                                                      b'\x55\x03' + bytes([self.get_sequence()]) + b'\x11', True)
            data = await self._client.read_gatt_char(SERVICE_UUID)
            humihex = data[6:8]
            temphex = data[4:6]
            temp10 = int.from_bytes(temphex, byteorder='little')
            humi10 = int.from_bytes(humihex, byteorder='little')
            self._temperature = float(temp10) / 100.0
            self._humidity = float(humi10) / 100.0
            if update_battery:
                await self._client.write_gatt_char(SERVICE_UUID,
                                                          b'\x55\x03' + bytes([self.get_sequence()]) + b'\x10',
                                                          True)
                data = await self._client.read_gatt_char(SERVICE_UUID)
                battery10 = data[4]
                self._battery = float(battery10) / 10.0
        except Exception as ex:
            _LOGGER.debug("Unexpected error: {}", ex)
        finally:
            self._lock.release()

    async def send_ir_raw(self, data):
        ir = data.strip()
        arr = ir.split(':', 1)
        return await self.send_ir(arr[0], arr[1])

    async def send_ir(self, key, ir_data):
        self._lock.acquire()
        sent = False
        try:
            await self._ensure_connected()
            sequence = self.get_sequence()
            await self._client.write_gatt_char(SERVICE_UUID,
                                               b'\x55' + bytes([len(a2b_hex(key)) + 3, sequence]) + b'\x03' + a2b_hex(
                                                   key), True)
            data = await self._client.read_gatt_char(SERVICE_UUID)
            if len(data) == 5 and data[4] == 1:
                sent = True
            else:
                send_list = []
                packet_count = int(len(ir_data) / 30) + 1
                if len(data) % 30 != 0:
                    packet_count += 1
                send_list.append(b'\x55' + bytes([len(a2b_hex(key)) + 5, sequence]) + b'\x00' + bytes(
                    [0, packet_count]) + a2b_hex(key))
                i = 0
                while i < packet_count - 1:
                    if len(ir_data) - i * 30 < 30:
                        send_ir_data = ir_data[i * 30:]
                    else:
                        send_ir_data = ir_data[i * 30:(i + 1) * 30]
                    send_list.append(b'\x55' + bytes([int(len(send_ir_data) / 2 + 4), sequence]) + b'\x00' + bytes(
                        [i + 1]) + a2b_hex(send_ir_data))
                    i += 1
                error = False
                for j in range(len(send_list)):
                    r = self._client.write_gatt_char(SERVICE_UUID, send_list[j], True)
                    if not r:
                        error = True
                        break
                if not error:
                    sent = True
        except Exception as ex:
            _LOGGER.debug("Unexpected error: {}", ex)
        finally:
            self._lock.release()
        return sent

    async def receive_ir(self, timeout=15):
        self._lock.acquire()
        self._receive_buffer = False
        self._received_packet = 0
        self._total_packet = -1
        try:
            await self._ensure_connected()
            sequence = self.get_sequence()
            await self._client.write_gatt_char(SERVICE_UUID, b'\x55\x03' + bytes([sequence]) + b'\x05', True)
            data = await self._client.read_gatt_char(SERVICE_UUID)
            if len(data) == 4 and data[3] == 7:
                await self._client.start_notify(SERVICE_UUID, self.handle_notification)
                # todo
                # while self._received_packet != self._total_packet:
                #     if not p.waitForNotifications(timeout):
                #         self._receive_buffer = False
                #         break
                await self._client.write_gatt_char(SERVICE_UUID, b'\x55\x03' + bytes([sequence]) + b'\x0b', True)
                await self._client.write_gatt_char(SERVICE_UUID, b'\x55\x03' + bytes([sequence]) + b'\x06', True)
            else:
                self._receive_buffer = False
        except Exception as ex:
            print("Unexpected error: {}".format(ex))
            self._receive_buffer = False
        finally:
            self._lock.release()
        return self._receive_buffer

    def handle_notification(self, characteristic, data):
        if characteristic.uuid == SERVICE_UUID:
            if len(data) > 4 and data[3] == 9:
                if data[4] == 0:
                    self._total_packet = data[5]
                    self._receive_buffer = []
                    self._received_packet += 1
                elif data[4] == self._received_packet:
                    self._receive_buffer.extend(data[5:])
                    self._received_packet += 1
                else:
                    self._receive_buffer = False
                    self._total_packet = -1
