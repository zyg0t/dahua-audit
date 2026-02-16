import socket
import struct
import time
from enum import Enum
import config

LOGIN_TEMPLATE = b'\xa0\x00\x00\x60%b\x00\x00\x00%b%b%b%b\x04\x01\x00\x00\x00\x00\xa1\xaa%b&&%b\x00Random:%b\r\n\r\n'
GET_PTZ = b'\xa4\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
GET_CHANNELS = b'\xa8\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
GET_SOUND = b'\xa4\x00\x00\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

class Status(Enum):
    SUCCESS = 0
    BLOCKED = 1
    FAILED = 2

class DahuaController:
    __slots__ = ('ip', 'port', 'login', 'password', 'model', 'channels_count', 'status', '_socket')

    def __init__(self, ip, port, login, password, timeout=config.DEFAULT_TIMEOUT):
        self.ip = ip
        self.port = int(port)
        self.login = login
        self.password = password
        self.model = "Unknown"
        self.channels_count = 0
        self.status = Status.FAILED
        self._socket = None

        try:
            self._connect(timeout)
        except Exception:
            self.status = Status.FAILED

    def _connect(self, timeout):
        try:
            self._socket = socket.create_connection((self.ip, self.port), timeout)
            self._socket.settimeout(timeout)
            self._login()
        except (socket.error, socket.timeout):
            self.status = Status.FAILED
            if self._socket:
                self._socket.close()

    def _login(self):
        login_bytes = self.login.encode('ascii')
        pass_bytes = self.password.encode('ascii')

        login_pad = (8 - len(self.login)) * b'\x00'
        pass_pad = (8 - len(self.password)) * b'\x00'

        timestamp = str(int(time.time())).encode('ascii')

        msg_len = struct.pack('b', 24 + len(self.login) + len(self.password))

        payload = LOGIN_TEMPLATE % (
            msg_len,
            login_bytes, login_pad,
            pass_bytes, pass_pad,
            login_bytes, pass_bytes,
            timestamp
        )

        self._socket.send(payload)
        data = self._socket.recv(128)

        if len(data) >= 10:
            if data[8] == 1 and data[9] == 4:
                self.status = Status.BLOCKED
            elif data[8] == 0:
                self.status = Status.SUCCESS
                self._fetch_info()
            else:
                self.status = Status.FAILED

    def _fetch_info(self):
        try:
            self._socket.send(GET_PTZ)
            data = self._receive_msg()
            if data:
                self.model = data.split(b'\x00')[0].decode('ascii', errors='ignore')

            self._socket.send(GET_CHANNELS)
            data = self._receive_msg()
            if data:
                self.channels_count = data.count(b'&&') + 1

            self._socket.send(GET_SOUND)
            data = self._receive_msg()
            if data and b'Dahua.Device.Record.General' in data:
                self.model += " (Audio)"

        except Exception:
            pass

    def _receive_msg(self):
        try:
            header = self._socket.recv(32)
            if not header or len(header) < 6:
                return None
            length = struct.unpack('<H', header[4:6])[0]
            return self._socket.recv(length)
        except Exception:
            return None

    def close(self):
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
