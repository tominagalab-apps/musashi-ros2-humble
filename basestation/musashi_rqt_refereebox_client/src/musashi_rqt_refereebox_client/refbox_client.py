from python_qt_binding.QtCore import QThread, Signal

import socket
from datetime import datetime, timezone
import json

from musashi_msgs.msg import PlayerState
from musashi_msgs.msg import PlayerStates

from musashi_rqt_refereebox_client import json_log

MAX_RECV_SIZE = 1024*4  # byte

class RefBoxClient(QThread):

    # シグナル定義
    recievedCommand = Signal(str, str)

    # コンストラクタ
    def __init__(self,):
        super(RefBoxClient, self).__init__()

        # ソケットの作成．ソケットはメンバ変数
        # IPv4, TCP設定
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._isRun = True

    # デストラクタ
    def __del__(self,):
        pass

    # 接続（サーバへのログイン）処理メソッド
    def connect(self, address, port):
        # 接続処理
        try:
            self._socket.settimeout(3)  # timeout [sec]
            self._socket.connect((address, port))
        except Exception as e:
            print(e)
            return False

        # 接続完了した時刻を記録する（UTC）
        self.connected_time = datetime.now(timezone.utc)

        # 無事にサーバ（RefereeBox）へ接続ができれば，RefereeBox側で反応がある
        return True  # 接続完了を表す

    # 切断処理メソッド
    def disconnect(self,):
        self._isRun = False
        self._socket.close()
        self.join()

    # レフェリーボックスへログデータ（json）を送信する関数
    # player_statesメッセージのデータを読み取ってレフェリーボックスに送信するjsonデータを作成する
    # 一度辞書型を作ってjsonモジュールを使って変換する方法をとる
    def send_jsonlog(self, player_states):
        # まずはヘッダーを作成する
        data = json_log.make_header(self.connected_time)  # dataは辞書型

        # ------------------------------
        # 以下，各プレイヤーの状態を読み取りながらリストを作っていく
        # ------------------------------

        # ロボットの状態についてリストを作成する．
        _players = []
        for player_state in player_states.players:
            _player = [
                player_state.id,
                player_state.position.position.x,
                player_state.position.position.y,
                player_state.position.position.z,
                player_state.position.orientation.x,
                player_state.position.orientation.y,
                player_state.position.orientation.z,
                player_state.position.orientation.w,
                player_state.moveto.position.x,
                player_state.moveto.position.y,
                player_state.moveto.position.z,
                player_state.moveto.orientation.x,
                player_state.moveto.orientation.y,
                player_state.moveto.orientation.z,
                player_state.moveto.orientation.w,
                player_state.haveball,
            ]
            _players.append(_player)

        # data辞書にリストを追加．キー名は'robots'
        data['robots'] = json_log.make_players(_players)

        # ボールについてリストを作成する．
        balls = []
        for player_state in player_states.players:
            _ball = [
                player_state.position.position.x,
                player_state.position.position.y,
                player_state.position.position.z,
                player_state.position.orientation.x,
                player_state.position.orientation.y,
                player_state.position.orientation.z,
                player_state.position.orientation.w,
                player_state.ball.distance,
                player_state.ball.angle
            ]
            balls.append(_ball)
        # data辞書にリストを追加．キー名は'balls'
        data['balls'] = json_log(balls)

        # 障害物についてリストを作成する．ただし大会規定のワールド座標系に合わせないといけないので座標変換が必要
        # チーム内xy軸の定義と大会ルールの定義は異なっている
        data_obstacles = []
        for i, player_state in enumerate(player_states.players):  # ロボット台数分の繰り返し
            _obstacle_data = {
                'position': [0.0, 0.0, 0.0],
                'velocity': [0.0, 0.0, 0.0],
                'radius': 0.25,
                'confidence': 1.0
            }
            data_obstacles.append(_obstacle_data)  # リストに追加
        # リストを追加．キー名は'obstacles'
        data['obstacles'] = data_obstacles

        # 辞書型からjsonデータへ変換（パラメータはテキトウ）
        json_data = json.dump(data, ensure_ascii=False, indent=4)

        # 送信処理
        self._socket.send(json_data.encode())  # encode()でバイナリデータに変換して送信

        return

    # 主となる処理（スレッド処理実態）
    def run(self,):
        # ブロッキングモード設定
        self._socket.settimeout(None)

        while self._isRun:
            # RefereeBoxからのコマンド受信待ち
            recv = self._socket.recv(MAX_RECV_SIZE)

            # コマンドは全てjson形式のテキストデータで送られてきます
            # データ末尾にはNULL（'\0'）が入れられているみたいです
            # 文字列（str）型の末尾１文字を削除している
            recv_json = json.loads(recv.decode('utf-8')[:-1])

            # recv_jsonは辞書型
            # キーは'command'と'targetTeam'の二つ，各値を取得する
            command = recv_json['command']
            targetTeam = recv_json['targetTeam']

            # シグナルの発行
            self.recievedCommand.emit(recv, command, targetTeam)
