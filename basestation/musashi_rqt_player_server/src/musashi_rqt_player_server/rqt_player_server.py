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

RATE_PLAYER_STATES_PUBLISH = 0.1  # player_statsのパブリッシュ周期[s]
RATE_TF_BROADCAST = 0.1  # 各プレイヤーのtfのブロードキャスト周期[s]
RATE_SEND_TO_PLAYERS = 0.1  # 各playerへのコマンド送信周期[s]

MAGENTA = 0
CYAN = 1

TEAM_COLOR = CYAN  # チームのカラーを設定する

ALPHA = 1
BETA = 2
GAMMA = 3
DELTA = 4
GOALIE = 5

ROLE_ASSIGN_METHOD = 0  # 0:static, 1:by distance between ball

TEAM_IP = '224.16.32.44'

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
        self._context = context  # 親クラスからコンテキストをもらう
        self._node = context.node  # 親クラスからノードの実態をもらう

        # レフェリーからのコマンド（musashi_msgs.msgのRefereeCmd型）
        self._refcmd = RefereeCmd()

        # チームの情報（プレイヤー情報の配列）
        self._player_states = PlayerStates()

        # チームカラー
        self._team_color = TEAM_COLOR

        # チームコマンドの初期化
        self.teamcmd = STOP

        # ウィジェットインスタンスを作成
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
        self.brs = [
            tf2_ros.TransformBroadcaster(self._node),
            tf2_ros.TransformBroadcaster(self._node),
            tf2_ros.TransformBroadcaster(self._node),
            tf2_ros.TransformBroadcaster(self._node),
            tf2_ros.TransformBroadcaster(self._node),
        ]

        # PlayerServer作成，シグナルスロット接続，起動
        self._player_server = PlayerServer()  # PlayerServerインスタンス作成
        self._player_server.recievedPlayerData.connect(
            self.onRecievedPlayerData)  # シグナルスロット接続
        try:
            self._player_server.open()  # プレイヤーサーバのオープン
        except Exception as e:
            self._node.get_logger().warning('{}'.format(e))
            self._node.get_logger().warning('Please confirm OWN_IP value in player_server.py')

        self._player_server.start()  # UDP通信の受信スレッド開始

        # GUIスレッドのスタート
        self.start_ui_thread()

        # PlayerStatesをパブリッシュするタイマコールバックのスタート
        self._node.timer_player_states_publish = self._node.create_timer(
            RATE_PLAYER_STATES_PUBLISH, self.timer_callback_player_states_publish)

        # tfをブロードキャストするタイマコールバックのスタート
        self._node.timer_tf_broadcast = self._node.create_timer(
            RATE_TF_BROADCAST, self.timer_callback_tf_broadcast)

        # 各プレイヤーへコマンドを送信するタイマコールバックのスタート
        self._node.timer_send_to_players = self._node.create_timer(
            RATE_SEND_TO_PLAYERS, self.timer_callback_send_to_players)

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

        # コンテキストに作成したウィジェットを追加
        # これをしないとGUI画面が表示されない
        self._context.add_widget(self._widget)

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
        self._node.get_logger().info(
            'command={}, targetTeam={}'.format(msg.command, msg.target_team))

        self._refcmd = msg  # メンバ変数に格納

        # hibikino-musashiチーム内のコマンドへ変換
        if self._refcmd.command == 'START':
            self.teamcmd = START
        elif self._refcmd.command == 'STOP':
            self.teamcmd = STOP
        elif self._refcmd.command == 'DROP_BALL':
            self.teamcmd = DROP_BALL
        elif self._refcmd.command == 'HALF_TIMER':
            pass
        elif self._refcmd.command == 'END_GAME':
            pass
        elif self._refcmd.command == 'GAME_OVER':
            pass
        elif self._refcmd.command == 'PARK':
            pass
        elif self._refcmd.command == 'FIRST_HALF':
            self.teamcmd = FIRST
        elif self._refcmd.command == 'SECOND_HALF':
            self.teamcmd = SECOND
        elif self._refcmd.command == 'FIRST_HALF_OVERTIME':
            pass
        elif self._refcmd.command == 'SECOND_HALF_OVERTIME':
            pass
        elif self._refcmd.command == 'WELCOME':
            self.teamcmd = WELCOME
        elif self._refcmd.command == 'KICKOFF':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    self.teamcmd = KICKOFF_M
                else:
                    self.teamcmd = KICKOFF_C
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    self.teamcmd = KICKOFF_C
                else:
                    self.teamcmd = KICKOFF_M
        elif self._refcmd.command == 'GOALKICK':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    self.teamcmd = GOAL_KICK_M
                else:
                    self.teamcmd = GOAL_KICK_C
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    self.teamcmd = GOAL_KICK_C
                else:
                    self.teamcmd = GOAL_KICK_M
        elif self._refcmd.command == 'THROWIN':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    self.teamcmd = THROWIN_M
                else:
                    self.teamcmd = THROWIN_C
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    self.teamcmd = THROWIN_C
                else:
                    self.teamcmd = THROWIN_M
        elif self._refcmd.command == 'CORNER':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    self.teamcmd = CORNER_KICK_M
                else:
                    self.teamcmd = CORNER_KICK_C
            else:  # 相手のコーナーキックなら
                if self._team_color == MAGENTA:
                    self.teamcmd = CORNER_KICK_C
                else:
                    self.teamcmd = CORNER_KICK_M
        elif self._refcmd.command == 'PENALTY':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    self.teamcmd = PENALTY_M
                else:
                    self.teamcmd = PENALTY_C
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    self.teamcmd = PENALTY_C
                else:
                    self.teamcmd = PENALTY_M
        elif self._refcmd.command == 'FREEKICK':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    self.teamcmd = FREE_KICK_M
                else:
                    self.teamcmd = FREE_KICK_C
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    self.teamcmd = FREE_KICK_C
                else:
                    self.teamcmd = FREE_KICK_M
        elif self._refcmd.command == 'GOAL':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    self.teamcmd = GOAL_M
                else:
                    self.teamcmd = GOAL_C
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    self.teamcmd = GOAL_C
                else:
                    self.teamcmd = GOAL_M
        elif self._refcmd.command == 'REPAIR':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self._refcmd.command == 'YELLOW_CARD':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self._refcmd.command == 'DOUBLE_YELLOW_CARD':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self._refcmd.command == 'RED_CARD':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self._refcmd.command == 'SUBSTITUTION':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
        elif self._refcmd.command == 'IS_ALIVE':
            if self._refcmd.target_team == TEAM_IP:
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
            else:  # 相手のキックオフなら
                if self._team_color == MAGENTA:
                    pass
                else:
                    pass
        else:
            pass

        # UI上に表示
        self._widget.lblTeamCmd.setText(str(self.teamcmd))
        return

    # PlayerStatesをパブリッシュするタイマコールバック関数
    def timer_callback_player_states_publish(self,):
        # player_statesメッセージをパブリッシュ
        self._pub_player_stats.publish(self._player_states)
        return

    def timer_callback_tf_broadcast(self,):

        # 各プレイヤーのtfをブロードキャスト
        now = self._node.get_clock().now().to_msg()

        trs = [
            TransformStamped(),
            TransformStamped(),
            TransformStamped(),
            TransformStamped(),
            TransformStamped(),
        ]

        for i, player in enumerate(self._player_states.players):
            trs[i].header.stamp = now
            trs[i].header.frame_id = 'world'
            trs[i].child_frame_id = 'player' + str(i + 1) + '/base_link'
            trs[i].transform.translation.x = player.position.position.x
            trs[i].transform.translation.y = player.position.position.y
            trs[i].transform.translation.z = player.position.position.z
            trs[i].transform.rotation.x = player.position.orientation.x
            trs[i].transform.rotation.y = player.position.orientation.y
            trs[i].transform.rotation.z = player.position.orientation.z
            trs[i].transform.rotation.w = player.position.orientation.w
            self.brs[i].sendTransform(trs[i])
            

        # for player_state in self._player_states.players:
        #     now = self._node.get_clock().now().to_msg()
        #     t = TransformStamped()

        #     t.header.stamp = now
        #     t.header.frame_id = 'world'
        #     t.child_frame_id = 'player' + str(player_state.id) + '/base_link'

        #     t.transform.translation.x = player_state.position.position.x
        #     t.transform.translation.y = player_state.position.position.y
        #     t.transform.translation.z = player_state.position.position.z
        #     t.transform.rotation.x = player_state.position.orientation.x
        #     t.transform.rotation.y = player_state.position.orientation.y
        #     t.transform.rotation.z = player_state.position.orientation.z
        #     t.transform.rotation.w = player_state.position.orientation.w

        #     # self.br.sendTransform(t)
        #     self.brs[player_state.id - 1].sendTransform(t)
        return

    def timer_callback_send_to_players(self,):

        # 返信内容はコマンド＋全プレイヤーのデータ
        send_data = struct.pack(
            'ii',
            5,  # aliveNum
            self._team_color,  # color
        )

        # commandリスト作成,結合
        send_data = send_data + struct.pack(
            'iiiii',
            self.teamcmd,
            self.teamcmd,
            self.teamcmd,
            self.teamcmd,
            self.teamcmd,
        )

        # stateリスト結合
        send_data = send_data + struct.pack(
            'iiiii',
            self._player_states.players[0].state,
            self._player_states.players[1].state,
            self._player_states.players[2].state,
            self._player_states.players[3].state,
            self._player_states.players[4].state
        )

        # ball_distanceリスト作成，結合
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].ball.distance,
            self._player_states.players[1].ball.distance,
            self._player_states.players[2].ball.distance,
            self._player_states.players[3].ball.distance,
            self._player_states.players[4].ball.distance,
        )

        # ball_angleリスト作成，結合
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].ball.angle,
            self._player_states.players[1].ball.angle,
            self._player_states.players[2].ball.angle,
            self._player_states.players[3].ball.angle,
            self._player_states.players[4].ball.angle,
        )

        # goal_distanceリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].goal.distance,
            self._player_states.players[1].goal.distance,
            self._player_states.players[2].goal.distance,
            self._player_states.players[3].goal.distance,
            self._player_states.players[4].goal.distance,
        )

        # goal_angleリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].goal.angle,
            self._player_states.players[1].goal.angle,
            self._player_states.players[2].goal.angle,
            self._player_states.players[3].goal.angle,
            self._player_states.players[4].goal.angle,
        )

        # my_goal.distanceリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].my_goal.distance,
            self._player_states.players[1].my_goal.distance,
            self._player_states.players[2].my_goal.distance,
            self._player_states.players[3].my_goal.distance,
            self._player_states.players[4].my_goal.distance,
        )

        # my_goal.angleリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].my_goal.angle,
            self._player_states.players[1].my_goal.angle,
            self._player_states.players[2].my_goal.angle,
            self._player_states.players[3].my_goal.angle,
            self._player_states.players[4].my_goal.angle,
        )

        # position.xリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].position.position.x,
            self._player_states.players[1].position.position.x,
            self._player_states.players[2].position.position.x,
            self._player_states.players[3].position.position.x,
            self._player_states.players[4].position.position.x,
        )
        # position.yリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].position.position.y,
            self._player_states.players[1].position.position.y,
            self._player_states.players[2].position.position.y,
            self._player_states.players[3].position.position.y,
            self._player_states.players[4].position.position.y,
        )
        # position.angleリスト作成，結合
        # クォータニオンからRPYに変換する必要がある
        send_data = send_data + struct.pack(
            'ddddd',
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        )

        # ロールの決定処理
        roles = self.roles_dicision()

        # roleリスト作成，結合
        send_data = send_data + struct.pack(
            'iiiii',
            roles[0],
            roles[1],
            roles[2],
            roles[3],
            roles[4],
        )

        # haveBallリスト作成，結合
        send_data = send_data + struct.pack(
            'iiiii',
            self._player_states.players[0].haveball,
            self._player_states.players[1].haveball,
            self._player_states.players[2].haveball,
            self._player_states.players[3].haveball,
            self._player_states.players[4].haveball
        )

        # moveto.xリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].moveto.position.x,
            self._player_states.players[1].moveto.position.x,
            self._player_states.players[2].moveto.position.x,
            self._player_states.players[3].moveto.position.x,
            self._player_states.players[4].moveto.position.x,
        )

        # moveto.yリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].moveto.position.y,
            self._player_states.players[1].moveto.position.y,
            self._player_states.players[2].moveto.position.y,
            self._player_states.players[3].moveto.position.y,
            self._player_states.players[4].moveto.position.y,
        )

        # moveto.angleリスト作成，結合
        # クォータニオンからRPYに変換する必要がある
        send_data = send_data + struct.pack(
            'ddddd',
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        )

        # oblstacle.distanceリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].obstacle.distance,
            self._player_states.players[1].obstacle.distance,
            self._player_states.players[2].obstacle.distance,
            self._player_states.players[3].obstacle.distance,
            self._player_states.players[4].obstacle.distance,
        )

        # obstacle.angleリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].obstacle.angle,
            self._player_states.players[1].obstacle.angle,
            self._player_states.players[2].obstacle.angle,
            self._player_states.players[3].obstacle.angle,
            self._player_states.players[4].obstacle.angle,
        )

        # state_vectorリスト作成，結合
        # 多分position（自己位置）のデータだったはず
        # position.xリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].position.position.x,
            self._player_states.players[1].position.position.x,
            self._player_states.players[2].position.position.x,
            self._player_states.players[3].position.position.x,
            self._player_states.players[4].position.position.x,
        )
        # position.yリスト作成，結合Ï
        send_data = send_data + struct.pack(
            'ddddd',
            self._player_states.players[0].position.position.y,
            self._player_states.players[1].position.position.y,
            self._player_states.players[2].position.position.y,
            self._player_states.players[3].position.position.y,
            self._player_states.players[4].position.position.y,
        )
        # position.angleリスト作成，結合
        # クォータニオンからRPYに変換する必要がある
        send_data = send_data + struct.pack(
            'ddddd',
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        )

        # 送信処理
        # print(len(send_data))
        try:
            self._player_server.broadcast(send_data)
        except Exception as e:
            self._node.get_logger().error(
                '{}: Please confirm Player IP address in player_server.py'.format(e))

        return

    # PlayerServerクラスからシグナルが発行された時に実行されるスロット
    # プレイヤーからデータを受信した際のスロット関数
    # id: 受信したプレイヤーのid
    # player_state: プレイヤーのデータ
    @Slot(int, PlayerState)
    def onRecievedPlayerData(self, id, player_state):
        self._node.get_logger().debug('Player No:{}, states={}'.format(id, player_state))
        player_state.header.stamp = self._node.get_clock().now().to_msg()
        self._player_states.players[id - 1] = player_state  # 配列に代入
        return

    def roles_dicision(self,):
        # 静的ロール割り振り
        roles = [ALPHA, BETA, GAMMA, DELTA, GOALIE]

        # -----
        # ここから頑張って各プレイヤーのロールを決定する処理
        # -----
        # （案１）ボールとの距離の近さ順にAlpha, Beta,...
        if ROLE_ASSIGN_METHOD == 1:

            # 各プレイヤーのIDとball.distanceをタプルにしてリスト化
            ball_distances = []
            for player in self._player_states.players:
                tmp = (player.id, player.ball.distance)
                if player.id != GOALIE:  # ゴーリーは除外する
                    ball_distances.append(tmp)

            # 昇順（近い順に）ソート
            ball_distances.sort(key=lambda x: x[1])

            # rolesを並び替え
            roles[ball_distances[0]] = ALPHA
            roles[ball_distances[1]] = BETA
            roles[ball_distances[2]] = GAMMA
            roles[ball_distances[3]] = DELTA

        # ロール決定処理ここまで
        return roles  # 結果
