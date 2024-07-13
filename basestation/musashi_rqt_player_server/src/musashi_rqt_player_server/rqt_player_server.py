import os
import struct
from ament_index_python.resources import get_resource
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget
from qt_gui.plugin import Plugin
from python_qt_binding.QtCore import QTimer, Slot

from musashi_rqt_player_server.player_server import PlayerServer

from geometry_msgs.msg import TransformStamped
from musashi_msgs.msg import RefereeCmd
from musashi_msgs.msg import PlayerState
from musashi_msgs.msg import PlayerStates

import tf2_ros

PKG_NAME = 'musashi_rqt_player_server'
UI_FILE_NAME = 'player_server.ui'

PUBLISH_RATE = 0.16  # 33Hz

TEAM_IP = '224.16.32.44'

MAGENTA = 0
CYAN = 1

# hibikino-musashiのチーム内コマンド
WELCOME = 00
START = 10
STOP = 11
FIRST = 20
SECOND = 21
KICKOFF_M = 30
KICKOFF_C = 40
THROWIN_M = 31
THROWIN_C = 41
CORNER_KICK_M = 32
CORNER_KICK_C = 42
GOAL_KICK_M = 33
GOAL_KICK_C = 43
FREE_KICK_M = 34
FREE_KICK_C = 44
PENALTY_M = 35
PENALTY_C = 45
GOAL_M = 36
GOAL_C = 46
DROP_BALL = 55
CALIB_COMPASS = 66


class RqtPlayerServer(Plugin):
    def __init__(self, context):
        super(RqtPlayerServer, self).__init__(context)

        self.setObjectName('RqtPlayerServer')
        self._context = context
        self._node = context.node

        # レフェリーからのコマンド（musashi_msgs.msgのRefereeCmd型）
        self.refcmd = RefereeCmd()

        # チームの情報（プレイヤー情報の配列）
        self.player_states = PlayerStates()

        # チームカラー
        self.team_color = CYAN

        # ウィジェットインスタンスを作成
        # メンバ変数_widgetに.uiファイルが書き込まれる
        self.create_ui()

        # サブスクライバー作成
        self._sub_refcmd = self._node.create_subscription(
            RefereeCmd,
            '/referee_cmd',
            self.refcmd_callback,
            10
        )

        # パブリッシャー作成
        self._pub_player_stats = self._node.create_publisher(
            PlayerStates,
            '/player_states',
            10
        )

        # tfブロードキャスター作成
        self.br = tf2_ros.TransformBroadcaster(self._node)

        # PlayerServer作成，シグナルスロット接続，起動
        self._player_server = PlayerServer()  # PlayerServerインスタンス作成
        self._player_server.recievedPlayerData.connect(
            self.onRecievedPlayerData)  # シグナルスロット接続
        self._player_server.open()  # プレイヤーサーバのオープン
        self._player_server.start()  # UDP通信の受信スレッド開始

        # コンテキストに作成したウィジェットを追加
        # これをしないとGUI画面が表示されない
        self._context.add_widget(self._widget)

        # GUIスレッドのスタート
        self.start_ui_thread()

        # PlayerStatesをパブリッシュするタイマコールバックのスタート
        self._node.timer = self._node.create_timer(
            PUBLISH_RATE, self.player_states_publish_timer_callback)

    def create_ui(self):
        # Qwidget型のメンバ変数作成
        self._widget = QWidget()
        # パッケージ名からパッケージのディレクトリパスを取得
        _, package_path = get_resource('packages', PKG_NAME)
        # .uiファイルへのパスを作成，取得
        ui_file = os.path.join(package_path, 'share',
                               PKG_NAME, 'resource', UI_FILE_NAME)
        # .uiファイルをQWidget型メンバ変数にロード
        loadUi(ui_file, self._widget)

        # 複数立ち上げた時の対策処理でウィンドウ名を変更している
        if self._context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % self._context.serial_number()))

    def start_ui_thread(self):
        # QTimerのtimeoutシグナルが発行されるたびにQWidgetのupdateスロットが実行される
        # これをしないと各ウィジェットのシグナルが発行された時に認識されない

        # GUIイベント更新のためのタイマ割り込み
        self._timer = QTimer()
        # timeoutシグナルをupdateスロットに接続
        self._timer.timeout.connect(self._widget.update)
        # 16msec周期（33Hz）で画面更新
        self._timer.start(16)

    def shutdown_plugin(self):
        # 終了時はタイマーを止める
        self._timer.stop()
        self._player_server.close()

    def save_settings(self, plugin_settings, instance_settings):
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        pass

    # レフェリーボックスコマンドのサブスクライバ-コールバック関数
    def refcmd_callback(self, msg):
        self._node.get_logger.info(msg.command, msg.target_team)
        self.refcmd = msg  # メンバ変数に格納

        # hibikino-musashiチーム内のコマンドへ変換
        if self.refcmd.command == 'START':
            self.teamcmd = START
        elif self.refcmd.command == 'STOP':
            self.teamcmd = STOP
        elif self.refcmd.command == 'DROP_BALL':
            self.teamcmd = DROP_BALL
        elif self.refcmd.command == 'HALF_TIMER':
            pass
        elif self.refcmd.command == 'END_GAME':
            pass
        elif self.refcmd.command == 'GAME_OVER':
            pass
        elif self.refcmd.command == 'PARK':
            pass
        elif self.refcmd.command == 'FIRST_HALF':
            self.teamcmd = FIRST
        elif self.refcmd.command == 'SECOND_HALF':
            self.teamcmd = SECOND
        elif self.refcmd.command == 'FIRST_HALF_OVERTIME':
            pass
        elif self.refcmd.command == 'SECOND_HALF_OVERTIME':
            pass
        elif self.refcmd.command == 'WELCOME':
            self.teamcmd = WELCOME
        elif self.refcmd.command == 'KICKOFF':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    self.teamcmd = KICKOFF_M
                else:
                    self.teamcmd = KICKOFF_C
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    self.teamcmd = KICKOFF_C
                else:
                    self.teamcmd = KICKOFF_M
        elif self.refcmd.command == 'GOALKICK':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    self.teamcmd = GOAL_KICK_M
                else:
                    self.teamcmd = GOAL_KICK_C
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    self.teamcmd = GOAL_KICK_C
                else:
                    self.teamcmd = GOAL_KICK_M
        elif self.refcmd.command == 'THROWIN':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    self.teamcmd = THROWIN_M
                else:
                    self.teamcmd = THROWIN_C
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    self.teamcmd = THROWIN_C
                else:
                    self.teamcmd = THROWIN_M
        elif self.refcmd.command == 'CORNER':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    self.teamcmd = CORNER_KICK_M
                else:
                    self.teamcmd = CORNER_KICK_C
            else:  # 相手のコーナーキックなら
                if self.team_color == MAGENTA:
                    self.teamcmd = CORNER_KICK_C
                else:
                    self.teamcmd = CORNER_KICK_M
        elif self.refcmd.command == 'PENALTY':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    self.teamcmd = PENALTY_M
                else:
                    self.teamcmd = PENALTY_C
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    self.teamcmd = PENALTY_C
                else:
                    self.teamcmd = PENALTY_M
        elif self.refcmd.command == 'GOAL':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    self.teamcmd = GOAL_M
                else:
                    self.teamcmd = GOAL_C
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    self.teamcmd = GOAL_C
                else:
                    self.teamcmd = GOAL_M
        elif self.refcmd.command == 'REPAIR':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self.refcmd.command == 'YELLOW_CARD':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self.refcmd.command == 'DOUBLE_YELLOW_CARD':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self.refcmd.command == 'RED_CARD':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self.refcmd.command == 'SUBSTITUTION':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self.refcmd.command == 'IS_ALIVE':
            if self.refcmd.target_team == TEAM_IP:
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self.team_color == MAGENTA:
                    pass
                else:
                    pass

        return

    # PlayerStatesをパブリッシュするタイマコールバック関数
    def player_states_publish_timer_callback(self,):
        # palyer_statesをパブリッシュ
        self._pub_player_stats.publish(self.player_states)

        # 各プレイヤーのtfをブロードキャスト
        for i, player_state in enumerate(self.player_states.players):
            now = self._node.get_clock().now().to_msg()
            t = TransformStamped()

            player_frame_id = 'player' + str(i+1) + '/base_link'

            t.header.stamp = now
            t.header.frame_id = 'map'
            t.child_frame_id = player_frame_id

            t.transform.translation.x = player_state.position.position.x
            t.transform.translation.y = player_state.position.position.y
            t.transform.translation.z = player_state.position.position.z
            t.transform.rotation.x = player_state.position.orientation.x
            t.transform.rotation.y = player_state.position.orientation.y
            t.transform.rotation.z = player_state.position.orientation.z
            t.transform.rotation.w = player_state.position.orientation.w

            self.br.sendTransform(t)

        return

    # PlayerServerクラスからシグナルが発行された時に実行されるスロット
    # プレイヤーからデータを受信した際のスロット関数
    # id: 受信したプレイヤーのid
    # player_state: プレイヤーのデータ
    @Slot(int, PlayerState)
    def onRecievedPlayerData(self, id, player_state):
        self._node.get_logger().debug('Player No:{}, states={}'.format(id, player_state))

        player_state.header.stamp = self._node.get_clock().now().to_msg()
        self.player_states.players[id - 1] = player_state  # 配列に代入

        # 受信したらプレイヤーへの返信
        # 返信内容はコマンド＋全プレイヤーのデータ

        # commandリスト作成
        command = [self.teamcmd]*5

        # stateリスト作成
        state = [
            self.player_states.players[0].state,
            self.player_states.players[1].state,
            self.player_states.players[2].state,
            self.player_states.players[3].state,
            self.player_states.players[4].state,
        ]
        
        # ball_distanceリスト作成
        ball_distance = [
            self.player_states.players[0].ball.distance,
            self.player_states.players[1].ball.distance,
            self.player_states.players[2].ball.distance,
            self.player_states.players[3].ball.distance,
            self.player_states.players[4].ball.distance,
        ]

        # ball_angleリスト作成
        ball_angle = [
            self.player_states.players[0].ball.angle,
            self.player_states.players[1].ball.angle,
            self.player_states.players[2].ball.angle,
            self.player_states.players[3].ball.angle,
            self.player_states.players[4].ball.angle,
        ]
        
        # goal_distanceリスト作成
        goal_distance = [
            self.player_states.players[0].goal.distance,
            self.player_states.players[1].goal.distance,
            self.player_states.players[2].goal.distance,
            self.player_states.players[3].goal.distance,
            self.player_states.players[4].goal.distance,
        ]
        
        # goal_distanceリスト作成
        goal_angle = [
            self.player_states.players[0].goal.angle,
            self.player_states.players[1].goal.angle,
            self.player_states.players[2].goal.angle,
            self.player_states.players[3].goal.angle,
            self.player_states.players[4].goal.angle,
        ]

        send_data = struct.pack(
            'iiiiiiiiiiiidddddddddddddddddddd',
            5,  # aliveNum
            self.team_color,  # color
            command,  # command[5] リストだとまとめて入らんかな...
            state, # state[5]
            ball_distance, # ball_distance[5]
            ball_angle, # ball_angle[5]
            goal_distance, # goal_distance[5]
            goal_angle, # goal_angle[5]
        )

        # 送信処理
        self._player_server.send(send_data)

        return
