from ament_index_python.resources import get_resource
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QHBoxLayout
from python_qt_binding.QtCore import QTimer, Slot
import os

from musashi_msgs.msg import PlayerStates

PKG_NAME = 'musashi_rqt_player_controller'
UI_FILE_NAME = 'player_controller.ui'

PLAYER_NUM = 5

MAGENTA = 0
CYAN = 1

ALPHA = 1
BETA = 2
GAMMA = 3
DELTA = 4
GOALIE = 5


class RqtPlayerController(Plugin):
    def __init__(self, context):
        super(RqtPlayerController, self).__init__(context)

        self.setObjectName('RqtPlayerController')
        self._context = context
        self._node = context.node

        # ウィジェットインスタンスを作成
        # メンバ変数_widgetに.uiファイルが書き込まれる
        self.create_ui()

        # コンテキストに作成したウィジェットを追加
        # これをしないとGUI画面が表示されない
        self._context.add_widget(self._widget)

        if color == MAGENTA:
            self._pwidgets[i].ledtDispColorAndRole.setStyleSheet(
            'background-color: magenta')
        elif color == CYAN:
            self._pwidgets[i].ledtDispColorAndRole.setStyleSheet(
            'background-color: cyan')

        if role == ALPHA:
            self._pwidgets[i].editRole.setText('Alpha')
        if role == BETA:
            self._pwidgets[i].editRole.setText('Beta')
        if role == GAMMA:
            self._pwidgets[i].editRole.setText('Gamma')
        if role == DELTA:
            self._pwidgets[i].editRole.setText('Delta')
        if role == GOALIE:
            self._pwidgets[i].editRole.setText('Goalie')

        return
