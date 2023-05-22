import sys, socket, threading
import requests
import time
from pyModbusTCP.client import ModbusClient
from PyQt5 import QtWidgets as QW
from PyQt5 import QtCore
from coi import Ui_Main

class my_app(QW.QMainWindow):
    def __init__(self):   #, parent=None):
        super().__init__()
        self.pConn = {
            '1': (('192.168.0.14', 23), 'self.ui.lblNexia'),
            '2': (('192.168.0.15', 22), 'self.ui.lblBosch'),
            '3': (('192.168.0.20', 80), 'self.ui.lblKramer1'),
            '4': (('192.168.0.31', 80), 'self.ui.lblKramer2'), # ????
            '5': (('192.168.0.11', 8000), 'self.ui.lblWatchout'),
            '6': (('192.168.0.31', 4001), 'self.ui.lbl3D1'), # 4001
#            '7': (('192.168.0.31', 4002), 'self.ui.lbl3D2'), # 4002
            '8': (('192.168.0.18', 4352), 'self.ui.lbl2D'),
            '9': (('192.168.0.13', 502), 'self.ui.lblLight'),
            '10': (('192.168.0.30', 80), 'self.ui.lblPower'),
            '11': (('192.168.0.28', 80), 'self.ui.lblibp'),
        }

        self.ui = Ui_Main()
        self.ui.setupUi(self)

        self.mon = QtCore.QTimer()
        self.mon.timeout.connect(self.Check_Conn)
        self.mon.start(5000)

        self.ui.butOn.clicked.connect(self.Power_On)   # включение комплекса
        self.ui.butOff.clicked.connect(self.Power_Off)  # выключение комплекса
        self.ui.sliderVolume.valueChanged.connect(self.Volume)  # общая громкость
        self.ui.butLight1.clicked.connect(lambda: self.Light_on_off(1))  # свет Люстра
        self.ui.butLight2.clicked.connect(lambda: self.Light_on_off(2))  # свет Потолок
        self.ui.butLight3.clicked.connect(lambda: self.Light_on_off(3))  # свет Вход
        self.ui.butLight4.clicked.connect(lambda: self.Light_on_off(4))  # свет БРА
        self.ui.butProj2D.clicked.connect(lambda: self.Proj_2d_power(False))  # отключение 2D
        self.ui.butProj3D.clicked.connect(lambda: self.Proj_3d_power(False))  # отключение 3D
        self.ui.butSCREENdown.clicked.connect(self.Screen_down)  #  экран ВНИЗ
        self.ui.butSCREENup.clicked.connect(self.Screen_up)  #  экран ВВЕРХ
        self.ui.radioConf.toggled.connect(self.Mode_Conf)  # режим конференции
        self.ui.radioPan.toggled.connect(self.Mode_Pan)   # режим панорамы
        self.ui.but2Dstart.clicked.connect(self.Video_2D_start) # старт ролика 2D
        self.ui.but2Dstop.clicked.connect(self.Video_2D_stop)  # стоп 2D
        self.ui.but3Dstart.clicked.connect(self.Video_3D_start)  # старт ролика 3D

        self.ui.checkSound1.stateChanged.connect(lambda: self.Sound_on_off(1))
        self.ui.checkSound2.stateChanged.connect(lambda: self.Sound_on_off(2))
        self.ui.checkSound3.stateChanged.connect(lambda: self.Sound_on_off(3))
        self.ui.checkSound4.stateChanged.connect(lambda: self.Sound_on_off(4))
        self.ui.sliderSound1.valueChanged.connect(lambda: self.Sound_slider(1))
        self.ui.sliderSound2.valueChanged.connect(lambda: self.Sound_slider(2))
        self.ui.sliderSound3.valueChanged.connect(lambda: self.Sound_slider(3))
        self.ui.sliderSound4.valueChanged.connect(lambda: self.Sound_slider(4))

    def Power_On(self):  #  включение комплекса
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.05)
            if sock.connect_ex(self.pConn['10'][0]) == 0:
                requests.get('http://192.168.0.30/hidden.htm?M0:O1=On&M0:O2=On&M0:O3=On&M0:O4=On&M0:O5=On&M0:O6=On&M0:O7=On&M0:O8=On')

    def Power_Off(self):  #  выключение комплекса
        self.PC_ShutDown()
        self.Proj_2d_power(False)
        self.Proj_3d_power(False)
        self.Screen_up()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.05)
            if sock.connect_ex(self.pConn['10'][0]) == 0:
                off_time = QtCore.QTimer()
                off_time.singleShot(60000, lambda:
                requests.get('http://192.168.0.30/hidden.htm?M0:O1=Off&M0:O2=Off&M0:O3=Off&M0:O4=Off&M0:O5=Off&M0:O6=Off&M0:O7=Off&M0:O8=Off'))
#            app.quit()

    def Volume(self):  #  Общая громкость
        print(f'Общая гровкость: {self.ui.sliderVolume.value()}')

    def Light_on_off(self, snum):     # переключение света и экрана
        mb_client = ModbusClient(host="192.168.0.13", port=502, timeout=0.1)
        if mb_client.open():
            bit = mb_client.read_coils(snum, 1)
            bit[0] = not bit[0]
            mb_client.write_single_coil(snum, bit[0])
            if bit[0]:
                command = f'self.ui.butLight{str(snum)}{self.ui.sNorm}'
            else:
                command = f'self.ui.butLight{str(snum)}{self.ui.sGreen}'
            eval(command)
        mb_client.close()

    def Screen_down(self):
        mb_client = ModbusClient(host="192.168.0.13", port=502, timeout=0.1)
        if mb_client.open():
            mb_client.write_single_coil(7, 0)
            mb_client.write_single_coil(6, 1)
        mb_client.close()

    def Screen_up(self):
        mb_client = ModbusClient(host="192.168.0.13", port=502, timeout=0.1)
        if mb_client.open():
            mb_client.write_single_coil(6, 1)
            mb_client.write_single_coil(7, 1)
        mb_client.close()

    def Proj_2d_power(self, mode):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(('192.168.0.18', 4352)) == 0:
                time.sleep(0.5)
                data = sock.recv(256)
                if mode:
                    data = b'%1POWR 1\r'
                    sock.send(data)
                    self.ui.butProj2D.setEnabled(True)
                else:
                    data = b'%1POWR 0\r'
                    sock.send(data)
                    self.ui.butProj2D.setStyleSheet("background-color: blue;")
                    self.ui.butProj2D.setEnabled(False)
                    cool_2d = threading.Thread(target=self.Proj_cooling, args=(1,), daemon=True)   # 1 - 2d-proj
                    cool_2d.start()

    def Proj_3d_power(self, mode):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.05)
            if sock.connect_ex(('192.168.0.31', 4001)) == 0:  # 3D1
                if mode:
                    data = b'\x02ADZZ;PON\x03'
                    sock.send(data)
                    self.ui.butProj3D.setEnabled(True)
                else:
                    data = b'\x02ADZZ;POF\x03'
                    sock.send(data)
                    self.ui.butProj3D.setEnabled(False)
#                    cool_3d = threading.Thread(target=self.Proj_cooling, args=(2,), daemon=True)  # 1 - 2d-proj
#                    cool_3d.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.05)
            if sock.connect_ex(('192.168.0.31', 4002)) == 0:   # 3D2
                if mode:
                    data = b'\x02ADZZ;PON\x03'
                    sock.send(data)
#                    self.ui.butProj3D.setEnabled(True)
                else:
                    data = b'\x02ADZZ;POF\x03'
                    sock.send(data)
#                    self.ui.butProj3D.setEnabled(False)

    def PC_ShutDown(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.05)
            if sock.connect_ex(('192.168.0.11', 4001)) == 0:
                data = b'shutdown_request'
                sock.send(data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.05)
            if sock.connect_ex(('192.168.0.12', 4001)) == 0:
                data = b'shutdown_request'
                sock.send(data)

    def Video_2D_start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(('192.168.0.11', 3039)) == 0:
                data = b'authenticate 1\r'
                sock.send(data)
                time.sleep(0.1) # ??? 0.5
                data = sock.recv(256)
                data = f'run "2d_video_{str(self.ui.combo2D.currentIndex()+1)}"\r'.encode('utf-8')
                sock.send(data)

    def Video_2D_stop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(('192.168.0.11', 3039)) == 0:
                data = b'authenticate 1\r'
                sock.send(data)
                time.sleep(0.1)
                data = sock.recv(256)
                data = f'run "stop"\r'.encode('utf-8')
                sock.send(data)

    def Video_3D_start(self):
        print(f'run "3d_video_{str(self.ui.combo3D.currentIndex()+1)}"')

    def Mode_Conf(self):   #  режим конференции
        self.Screen_down()
        self.Proj_2d_power(True)
        self.Proj_3d_power(False)
        self.ui.grComm.setEnabled(True)
        self.ui.gr2D.setEnabled(False)
        self.ui.gr3D.setEnabled(False)
        self.ui.grVic.setEnabled(False)

    def Mode_Pan(self):   #  режим панорамы
        self.Screen_up()
        self.Proj_2d_power(False)
        self.Proj_3d_power(True)
        self.ui.grComm.setEnabled(False)
        self.ui.gr2D.setEnabled(True)
        self.ui.gr3D.setEnabled(True)
        self.ui.grVic.setEnabled(True)

    def Proj_cooling(self, proj):   #  может попробовать через singleshot
        if proj == 1:   # 2d
            while True:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    if sock.connect_ex(('192.168.0.18', 4352)) == 0:
                        time.sleep(0.5)
                        data = sock.recv(256)
                        data = b'%1POWR ?\r'
                        sock.send(data)
                        time.sleep(0.5)
                        data = sock.recv(256)
                        if data == b'%1POWR=2\r':
                            time.sleep(5)
                        else:
                            break
                    else:
                        break
            self.ui.butProj2D.setStyleSheet("")
        else:   #  3d
            self.ui.butProj3D.setStyleSheet("")
            pass

    def Check_Conn(self):            # проверка связи с усьройствами
        for key, conn in self.pConn.items():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.01)
                if sock.connect_ex(conn[0]) == 0:  # Если  доступен
                    self.Check_Conn_Status(key, True)
                else:    # если не доступен
                    self.Check_Conn_Status(key, False)

    def Check_Conn_Status(self, obj, status):      # проверка связи с устр., установка цвета отображения
        command = self.pConn[obj][1] + self.ui.sGreen if status else self.pConn[obj][1] + self.ui.sRed
        eval(command)

    def Sound_on_off(self, snum):   # вкл/выкл звука
        if eval(f'self.ui.checkSound{snum}.isChecked()'):
            eval(f'self.ui.sliderSound{snum}.setEnabled(True)')
        else:
            eval(f'self.ui.sliderSound{snum}.setEnabled(False)')

    def Sound_slider(self, snum):  # громкость звука
        print(f"Громкость {snum}, уровень: {eval(f'self.ui.sliderSound{snum}.value()')}")


app = QW.QApplication(sys.argv)
window = my_app()
window.show()
app.exec_()
