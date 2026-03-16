

import os
from ament_index_python.resources import get_resource
from python_qt_binding import loadUi
from qt_gui.plugin import Plugin
from python_qt_binding.QtWidgets import QWidget, QErrorMessage, QApplication
from python_qt_binding.QtCore import QTimer, Qt

from musashi_rqt_refereebox_client.refereebox_tcp_client import (
    RefereeBoxTcpClient,
)
from musashi_rqt_refereebox_client.ros_bridge import RosBridge

PKG_NAME = 'musashi_rqt_refereebox_client'
UI_FILE_NAME = 'refereebox_client.ui'
DEFAULT_GUI_UPDATE_PERIOD = 0.033  # GUI update period [s]
DEFAULT_PLAYER_STATES_SEND_PERIOD = 0.25  # Timer callback period [s]


class RefereeBoxClientPlugin(Plugin):
    def __init__(self, context):
        """Initialize the rqt plugin, UI, and integrate TCP/ROS2 modules."""
        super().__init__(context)
        self.setObjectName('RefereeBoxClientPlugin')
        self._context = context
        self._node = context.node
        self.is_connected_refbox = False
        self._refbox_client = None
        self.player_states = None

        (
            self.gui_update_period,
            self.player_states_send_period,
        ) = self.load_period_parameters()

        self.create_ui()
        self.connect_signals_slots()
        # ROS2通信インターフェースを生成
        self.ros = RosBridge(
            self._node,
            player_states_callback=self.player_states_callback,
        )
        self._node.timer = self._node.create_timer(
            self.player_states_send_period, self.timer_callback
        )
        self.start_ui_thread()

    def _validate_positive_float(self, value, fallback, key_name):
        try:
            fval = float(value)
            if fval <= 0.0:
                raise ValueError('must be > 0')
            return fval
        except Exception:
            self._node.get_logger().warn(
                f'Invalid value for {key_name}: {value}. '
                f'Use fallback {fallback}'
            )
            return fallback

    def load_period_parameters(self):
        """Load timer periods from ROS2 parameters with fallback defaults."""
        if not self._node.has_parameter('gui_update_period_sec'):
            self._node.declare_parameter(
                'gui_update_period_sec', DEFAULT_GUI_UPDATE_PERIOD
            )
        if not self._node.has_parameter('player_states_send_period_sec'):
            self._node.declare_parameter(
                'player_states_send_period_sec',
                DEFAULT_PLAYER_STATES_SEND_PERIOD,
            )

        gui_update_period = self._validate_positive_float(
            self._node.get_parameter('gui_update_period_sec').value,
            DEFAULT_GUI_UPDATE_PERIOD,
            'gui_update_period_sec',
        )
        player_states_send_period = self._validate_positive_float(
            self._node.get_parameter(
                'player_states_send_period_sec'
            ).value,
            DEFAULT_PLAYER_STATES_SEND_PERIOD,
            'player_states_send_period_sec',
        )

        self._node.get_logger().info(
            'Loaded periods from ROS2 parameters: '
            f'gui_update_period_sec={gui_update_period}, '
            f'player_states_send_period_sec={player_states_send_period}'
        )

        return gui_update_period, player_states_send_period

    def create_ui(self):
        """Load and set up the Qt UI from .ui file, and display host IP."""
        self._widget = QWidget()
        _, package_path = get_resource('packages', PKG_NAME)
        ui_file = os.path.join(
            package_path, 'share', PKG_NAME, 'resource', UI_FILE_NAME
        )
        loadUi(ui_file, self._widget)
        if self._context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle()
                + f' ({self._context.serial_number()})'
            )
        self._context.add_widget(self._widget)
        try:
            host_ip = RefereeBoxTcpClient().getHostIP()
        except Exception:
            host_ip = '127.0.0.1'
        self._widget.lblOwnIP.setText(host_ip)

    def connect_signals_slots(self):
        """Connect Qt signals to their respective slots."""
        self._widget.chckConnect.stateChanged.connect(
            self.onStateChangedChckConnect
        )

    def start_ui_thread(self):
        """Start a QTimer to periodically update the Qt UI widgets."""
        self._timer = QTimer()
        self._timer.timeout.connect(self._widget.update)
        self._timer.start(int(self.gui_update_period * 1000.0))

    def shutdown_plugin(self):
        """Clean up resources and disconnect RefBoxClient on shutdown."""
        self._timer.stop()
        self.disconnect_refbox()

    def timer_callback(self):
        """Periodically send player_states to RefBox if connected."""
        if self.is_connected_refbox and self.player_states is not None:
            try:
                self._refbox_client.send_jsonlog(self.player_states)
            except Exception as e:
                self._node.get_logger().error(
                    f'Failed to send json log: {e}'
                )

    def onStateChangedChckConnect(self, state):
        """Handle connect/disconnect checkbox state change."""
        if state:
            self.connect_refbox()
        else:
            self.disconnect_refbox()

    def connect_refbox(self):
        """Attempt to connect to the RefereeBox and set up callbacks."""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self._refbox_client = RefereeBoxTcpClient()
            refboxIP = self._widget.lnedtIP.text()
            refboxPort = int(self._widget.lnedtPort.text())
            self._node.get_logger().info(
                f'Try to connect to RefereeBox [{refboxIP}:{refboxPort}] ...'
            )
            isConnect = self._refbox_client.connect(refboxIP, refboxPort)
            if isConnect:
                self._node.get_logger().info(
                    'Successfully connected to RefereeBox'
                )
                self._refbox_client.recievedCommand.connect(
                    self.onRecievedCommand
                )
                self._refbox_client.start()
                self.is_connected_refbox = True
            else:
                self._node.get_logger().error(
                    'Failed to connect to RefereeBox'
                )
                dlg = QErrorMessage(self._widget)
                dlg.showMessage(
                    'Failed to connect to RefereeBox. '
                    'Please check network connection status.'
                )
                self._widget.chckConnect.setCheckState(False)
                self.disconnect_refbox()
        finally:
            QApplication.restoreOverrideCursor()

    def disconnect_refbox(self):
        """Safely disconnect from RefereeBox and clean up client instance."""
        try:
            if self._refbox_client is not None:
                self._refbox_client.disconnect()
        except Exception:
            self._node.get_logger().error(
                'Error during disconnect of RefBoxClient'
            )
        finally:
            self._refbox_client = None
            self.is_connected_refbox = False

    def onRecievedCommand(self, recv, command, targetTeam):
        """Handle command from RefereeBox and publish RefereeCmd message."""
        self._node.get_logger().info(
            f'Recieved: command={command}, targetTeam={targetTeam}'
        )
        # Update the structured display
        self._widget.lblCommand.setText(command)
        self._widget.lblTargetTeam.setText(
            targetTeam if targetTeam else "All Teams"
        )
        # Display full JSON in the text browser with pretty formatting
        try:
            import json
            json_data = json.loads(recv.decode('utf-8'))
            pretty_json = json.dumps(
                json_data, indent=2, ensure_ascii=False
            )
            self._widget.txtRecv.setText(pretty_json)
        except json.JSONDecodeError:
            self._widget.txtRecv.setText(
                recv.decode('utf-8')
            )
        # ROS2インターフェース経由でRefereeCmdをpublish
        self.ros.publish_refcmd(command, targetTeam)

    def player_states_callback(self, player_states):
        """Store latest PlayerStates message for periodic sending."""
        self.player_states = player_states

    def save_settings(self, plugin_settings, instance_settings):
        """Save plugin settings (not used)."""
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        """Restore plugin settings (not used)."""
        pass


# Backward compatibility alias
RqtRefereeBoxClient = RefereeBoxClientPlugin
