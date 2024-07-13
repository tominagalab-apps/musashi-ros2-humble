import os
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

class RqtPlayerServer(Plugin):
    def __init__(self, context):
        super(RqtPlayerServer, self).__init__(context)

        self.setObjectName('RqtPlayerServer')
        self._context = context
        self._node = context.node

        # チームの情報（プレイヤー情報の配列）
        self.player_states = PlayerStates()

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

    # refereebox_clientがパブリッシュした，レフェリーボックスコマンドのサブスクライバー
    def refcmd_callback(self, msg):
        self._node.get_logger.info(msg.command, msg.target_team)

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

        # tfの作成とブロードキャスト

        return
