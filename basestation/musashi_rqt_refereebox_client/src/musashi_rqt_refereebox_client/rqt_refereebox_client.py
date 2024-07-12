import os
from ament_index_python.resources import get_resource
from python_qt_binding import loadUi
from qt_gui.plugin import Plugin
from python_qt_binding.QtWidgets import QWidget
from python_qt_binding.QtCore import QTimer, Slot
from python_qt_binding.QtWidgets import QErrorMessage

# from refereebox_client.refereebox_client_widget import RefereeBoxClientWidget
from musashi_rqt_refereebox_client.refbox_client import RefBoxClient

from musashi_msgs.msg import RefereeCmd

PKG_NAME = 'musashi_rqt_refereebox_client'
UI_FILE_NAME = 'refereebox_client.ui'

class RqtRefereeBoxClient(Plugin):
  def __init__(self, context):
    # 親クラス(Pluginクラス)のコンストラクタ呼び出し
    super(RqtRefereeBoxClient, self).__init__(context)
    
    # 自分の名前を設定
    self.setObjectName('RqtRefereeBoxClient')
    # コンテキストとノードのインスタンスを取得
    self._context = context
    self._node = context.node
    
    # ウィジェットインスタンスを作成
    # メンバ変数_widgetに.uiファイルが書き込まれる
    self.create_ui()
    
    # GUIシグナルスロット接続
    # connectボタンの状態変化時のシグナルスロット接続
    self._widget.chckConnect.stateChanged.connect(self.onStateChangedChckConnect)
    
    # パブリッシャー作成
    # レフェリーからのコマンドをRefereeCmdメッセージでパブリッシュするためのパブリッシャーを定義
    self._pub_refcmd = self._node.create_publisher(RefereeCmd, '/referee_cmd', 5)
    
    # コンテキストに作成したウィジェットを追加
    # これをしないとGUI画面が表示されない
    self._context.add_widget(self._widget)  
    
    # GUIスレッドのスタート
    self.start_ui_thread()
  
  # ウィジェット作成
  def create_ui(self):
    # Qwidget型のメンバ変数作成
    self._widget = QWidget()
    # パッケージ名からパッケージのディレクトリパスを取得
    _, package_path = get_resource('packages', PKG_NAME)
    # .uiファイルへのパスを作成，取得
    ui_file = os.path.join(package_path, 'share', PKG_NAME, 'resource', UI_FILE_NAME)
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
  
  # シャットダウン時処理
  def shutdown_plugin(self):
    # 終了時はタイマーを止める
    self._timer.stop()
  
  # プラグインの設定保存処理
  def save_settings(self, plugin_settings, instance_settings):
    pass
  
  # プラグインの設定保存処理
  def restore_settings(self, plugin_settings, instance_settings):
    pass

  #
  # 以下，スロット関数
  #
  # 接続チェックボックスの状態が変化した時に呼び出されるスロット  
  def onStateChangedChckConnect(self, state):
    if state: # チェックが入った → 接続処理
      
      # RefBoxClientの新規作成
      self._refbox_client = RefBoxClient()
      # IPアドレスとポートをGUIから取得
      refboxIP = self._widget.lnedtIP.text()
      refboxPort = int(self._widget.lnedtPort.text())
      
      # 接続のトライ
      self._node.get_logger().info('Try to connect to RefereeBox [{}:{}] ...'.format(refboxIP, refboxPort))
      isConnect = self._refbox_client.connect(refboxIP, refboxPort)
      
      if isConnect: # 接続成功時の処理
        self._node.get_logger().info('Successfully connected to RefereeBox')
        # レフェリーからコマンド受信時のシグナルスロット接続
        self._refbox_client.recievedCommand.connect(self.onRecievedCommand) 
        # RefereeBox client スレッドのスタート
        self._refbox_client.start() 

      else: # 接続失敗時の処理
        self._node.get_logger().error('Failed to connect to RefereeBox')
        self._node.get_logger().error('Please check network connection status')
        
        # エラーメッセージダイアログの表示
        dlg = QErrorMessage(self._widget)
        dlg.showMessage('Failed to connect to RefereeBox. Please check network connection status.')
        
        self._widget.chckConnect.setCheckState(False)
        self._refbox_client = None
        
    else: # チェックが外れた → 切断処理
      # self._refbox_client.disconnect()
      # self._refbox_client.join()
      self._refbox_client = None # デストラクタの呼び出し
      # pythonでは一応自動的にメモリ解放されるっぽい
      
  # refereebox_clientがrefereeboxから受信した際に呼び出されるスロット関数
  def onRecievedCommand(self, recv, command, targetTeam):
    self._node.get_logger().info('Recieved from RefereeBox')
    self._node.get_logger().info('command = {}, targetTeam = {}'.format(command, targetTeam))
    
    # GUIに受信した生テキストを表示
    self._widget.txtRecv.setText(recv)
    
    # メッセージの作成
    refereeCmd = RefereeCmd() # musashi_msgsパッケージで作成済み
    # 値の代入
    refereeCmd.command = command
    refereeCmd.target_team = targetTeam
    # パブリッシュ．player_serverのノードに伝達することが主目的
    self._pub_refcmd.publish(refereeCmd)
    