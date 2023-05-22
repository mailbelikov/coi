import socket
from pyModbusTCP.client import ModbusClient

class Projector:    # Базовый класс проекторов
    def __init__(self, host):     # host - ('ip', port)
        self.address = host[0]
        self.port = host[1]

    def online(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)
            if sock.connect_ex((self.address, self.port)) == 0:
                return True
            else:
                return False

class Projector_2D(Projector):      # Проектор 2D
    def __init__(self, host):
        super().__init__(host)

    def power(self, mode):     # True - ON; False - OFF
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((self.address, self.port)) == 0:
                time.sleep(0.1)
                _ = sock.recv(256)
                if mode: data = b'%1POWR 1\r'    # power ON
                else:  data = b'%1POWR 0\r'     # power OFF
                sock.send(data)

    def status(self):           # 0 - off, 1 - on, 2 - cooling
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((self.address, self.port)) == 0:
                _ = sock.recv(256)
                data = b'%1POWR ?\r'
                sock.send(data)
                time.sleep(0.1)
                data = sock.recv(256)
                if data == b'%1POWR=0\r': return 0  # выключен
                elif data == b'%1POWR=1\r': return 1  # включен
                elif data == b'%1POWR=2\r': return 2  # охлаждается


class Projector_3D(Projector):      # Проектор 3D
    def __init__(self, host):
        super().__init__(host)

    def power(self, mode):     # True - ON; False - OFF
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((self.address, self.port)) == 0:
                if mode:
                    data = b'\x02ADZZ;PON\x03'  # Включить
                else:
                    data = b'\x02ADZZ;POF\x03'    # Выключить
                sock.send(data)

    def mode_3d(self, mode):        # True - 3D, False - 2D
        pass


class Relay:            # Группа реле (управление светом и экраном)
    def __init__(self, ip_addr):
        self.address = ip_addr

    def online(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((self.address, 502) == 0:
                return True
            else:
                return False

    def contact(self, number, mode):        # Номер реле, True/False - Вкл/ выкл
        mb_client = ModbusClient(host=self.address, port=502, timeout=0.1)
        if mb_client.open():
            mb_client.write_single_coil(number, mode)
        mb_client.close()

    def status(self, number):  # Номер реле
        mb_client = ModbusClient(host=self.address, port=502, timeout=0.1)
        if mb_client.open():
            result = mb_client.read_coils(number, 1)
        mb_client.close()
        return result[0]


class Video_server:
    def __init__(self, host):
        self.address = host[0]
        self.port = host[1]

    def stop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((self.address, self.port)) == 0:
                data = b'authenticate 1\r'
                sock.send(data)
                time.sleep(0.1)
                data = sock.recv(256)
                data = f'run "stop"\r'.encode('utf-8')
                sock.send(data)

    def start(self, video):         # video - имя видео ('2d_video_1', '3d_video_2')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((self.address, self.port)) == 0:
                data = b'authenticate 1\r'
                sock.send(data)
                time.sleep(0.1) # ??? 0.5
                data = sock.recv(256)
                data = f'run "{video}"\r'.encode('utf-8')
                sock.send(data)

    def poweroff(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.1)
            if sock.connect_ex((self.address, 4001)) == 0:
                data = b'shutdown_request'
                sock.send(data)



