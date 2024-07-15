from python_qt_binding.QtCore import QThread, Signal

import socket
import math
from musashi_msgs.msg import PlayerState

OWN_IP = '127.0.0.1'  # basestation自身のIPアドレス
# OWN_IP = '172.16.44.10'

PORT = 12536  # ポート

# 各プレイヤーのIPアドレス
PLAYER1_IP = '172.16.44.1'
PLAYER2_IP = '172.16.44.2'
PLAYER3_IP = '172.16.44.3'
PLAYER4_IP = '172.16.44.4'
PLAYER5_IP = '172.16.44.5'

MAX_RECV_SIZE = 1024*4

class PlayerServer(QThread):

    # シグナル定義
    recievedPlayerData = Signal(int, PlayerState)

    # コンストラクタ
    def __init__(self):
        super(PlayerServer, self).__init__()

        # ソケットの作成．ソケットはメンバ変数
        # IPv4, UDP設定
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # プレイヤーデータリスト
        self._players = [{}, {}, {}, {}, {}]

        self._isRun = True

       # デストラクタ
    def __del__(self,):
        pass

    def open(self,):
        # バインド（紐付け）
        self._socket.bind((OWN_IP, PORT))

    def close(self,):
        self._isRun = False

    def run(self,):
        # プレイヤーからの受信スレッド
        self._socket.settimeout(None)

        while self._isRun:
            # 受信処理（ブロッキングモード）
            print('wait player ...')
            recv, addr = self._socket.recvfrom(MAX_RECV_SIZE)
            # recvには受信したデータ（文字列）
            # addrには送信元のアドレス（文字列）が入っている

            # addrから送信元のプレイヤーのIDを割り出す
            # IPアドレスの下1桁でわかる
            player_no = int(addr[0].split('.')[-1])

            # recvの文字列をカンマでスプリットする
            recv_str = recv.decode()  # bytesオブジェクトからstrオブジェクトへ変換

            if recv_str[0] == 'R' or recv_str[0] == 'P':
                continue

            values = recv_str.split(',')  # カンマで分割処理->文字列オブジェクトのリストオブジェクトになる

            # PlayerState型に値を代入
            player_state = PlayerState()

            player_state.color = int(values[0])
            player_state.id = int(values[1])
            player_state.action = int(values[2])
            player_state.state = int(values[3])
            player_state.ball.distance = float(values[4])
            player_state.ball.angle = float(values[5])
            player_state.goal.distance = float(values[6])
            player_state.goal.angle = float(values[7])
            player_state.my_goal.distance = float(values[8])
            player_state.my_goal.angle = float(values[9])

            player_state.position.position.x = float(values[10])
            player_state.position.position.y = float(values[11])
            angle = float(values[12])
            [qx, qy, qz, qw] = self.euler_to_quaternion(0, 0, angle)
            player_state.position.orientation.x = qx
            player_state.position.orientation.y = qy
            player_state.position.orientation.z = qz
            player_state.position.orientation.w = qw

            player_state.role = int(values[13])
            player_state.haveball = int(values[14])

            player_state.moveto.position.x = float(values[15])
            player_state.moveto.position.y = float(values[16])
            angle = float(values[17])
            [qx, qy, qz, qw] = self.euler_to_quaternion(0, 0, angle)
            player_state.moveto.orientation.x = qx
            player_state.moveto.orientation.y = qy
            player_state.moveto.orientation.z = qz
            player_state.moveto.orientation.w = qw

            player_state.obstacle.distance = float(values[18])
            # player_state.obstacle.angle = float(values[19])

            # シグナル発行
            self.recievedPlayerData.emit(player_state.id, player_state)

    def broadcast(self, binary_data):
        try:
            self._socket.sendto(binary_data, (PLAYER1_IP, PORT))
            self._socket.sendto(binary_data, (PLAYER2_IP, PORT))
            self._socket.sendto(binary_data, (PLAYER3_IP, PORT))
            self._socket.sendto(binary_data, (PLAYER4_IP, PORT))
            self._socket.sendto(binary_data, (PLAYER5_IP, PORT))
        except Exception as e: 
            # ローカルループバックテスト(OWN_IP=127.0.0.1)の時は例外が出るので対処している
            return
        
        return

    def euler_to_quaternion(self, roll, pitch, yaw):
        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - \
            math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + \
            math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - \
            math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + \
            math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        return [qx, qy, qz, qw]
