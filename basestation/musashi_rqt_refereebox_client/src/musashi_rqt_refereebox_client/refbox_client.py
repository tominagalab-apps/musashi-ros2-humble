from python_qt_binding.QtCore import QThread, Signal

import sys
import socket
import threading
import time
import json

from musashi_msgs.msg import PlayerState
from musashi_msgs.msg import PlayerStates

TEAM_IP = '172.16.32.44' # チームに割り振られた固有IP（コーチボックスに設定するアドレスではありません）
MAX_RECV_SIZE = 1024*4 # byte

class RefBoxClient(QThread):
  
  # シグナル定義
  recievedCommand = Signal(str,str)
  
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
      self._socket.settimeout(3) # timeout [sec]
      self._socket.connect((address, port))
    except Exception as e:
      print(e)
      return False
    
    # 無事にサーバ（RefereeBox）へ接続ができれば，RefereeBox側で反応がある
    return True # 接続完了を表す
    
  # 切断処理メソッド
  def disconnect(self,):
    self._isRun = False
    self._socket.close()
    self.join()
    
  # レフェリーボックスへログデータ（json）を送信する関数
  def send_log(self, player_states):
    
    # player_statesメッセージのデータを読み取ってレフェリーボックスに送信するjsonデータを作成する
    # やり方として一度辞書型を作ってjsonモジュールを使って変換する方法をとる
    
    data = {
      'type': 'worldstate', # これは決まっている
      'teamName': 'Hibikino-Musashi', # これは決まっている
      'intention': '', # 自由な記入形式（使わなくてもいい）チーム全体の意思決定のメモみたいな
      # 'ageMs': 
    }
    
    #------------------------------ 
    # 以下，各プレイヤーの状態を読み取りながらリストを作っていく
    #------------------------------
    
    # ロボットの状態についてリストを作成する．ただし大会規定のワールド座標系に合わせないといけないので座標変換が必要
    # チーム内xy軸の定義と大会ルールの定義は異なっている
    data_players = []
    for i,player_state in enumerate(player_states.players): # ロボット台数分の繰り返し
      _player_data = {
        'id': int(player_state.id), # プレイヤーID（整数型）
        'pose': [0.0,0.0,0.0],
        'targetPose': [0.0,0.0,0.0],
        'velocity': [0.0,0.0,0.0],
        'intention': '',
        'batteryLevel': 95.0,
        'ballEngaged': int(player_state.haveball) # ホール保持の有無（0:未保持，1:保持）
      }
      data_players.append(_player_data) # リストに追加
    data['robots'] = data_players # リストを追加．キー名は'robots'
    
    # ボールについてリストを作成する．ただし大会規定のワールド座標系に合わせないといけないので座標変換が必要
    # チーム内xy軸の定義と大会ルールの定義は異なっている
    data_balls = []
    for i,player_state in enumerate(player_states.players): # ロボット台数分の繰り返し
      _ball_data = {
        'position': [0.0,0.0,0.0],
        'velocity': [0.0,0.0,0.0],
        'confidence': 1.0
      }
      data_balls.append(_ball_data) # リストに追加
    data['balls'] = data_balls # リストを追加．キー名は'balls'
    
    # 障害物についてリストを作成する．ただし大会規定のワールド座標系に合わせないといけないので座標変換が必要
    # チーム内xy軸の定義と大会ルールの定義は異なっている
    data_obstacles = []
    for i,player_state in enumerate(player_states.players): # ロボット台数分の繰り返し
      _obstacle_data = {
        'position': [0.0,0.0,0.0],
        'velocity': [0.0,0.0,0.0],
        'radius': 0.25,
        'confidence': 1.0
      }
      data_obstacles.append(_obstacle_data) # リストに追加
    data['obstacles'] = data_obstacles # リストを追加．キー名は'obstacles'
    
    
    # 辞書型からjsonデータへ変換（パラメータはテキトウ）
    json_data = json.dump(data, ensure_ascii=False, indent=4)
    
    # 送信処理
    self._socket.send(json_data.encode()) # encode()でバイナリデータに変換して送信
    
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