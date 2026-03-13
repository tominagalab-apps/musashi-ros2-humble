"""
ros_interface.py
ROS2のPublisher/Subscriber/Service通信をまとめるインターフェースモジュール
"""

from musashi_msgs.msg import RefereeCmd, PlayerStates

class RosInterface:
    def __init__(self, node, refcmd_callback=None, player_states_callback=None):
        """ROS2通信の初期化。必要に応じてコールバックを登録。"""
        self._node = node
        self._pub_refcmd = self._node.create_publisher(RefereeCmd, '/referee_cmd', 5)
        self._sub_player_states = self._node.create_subscription(
            PlayerStates, '/player_states', self._on_player_states, 5)
        self._user_player_states_callback = player_states_callback
        self._user_refcmd_callback = refcmd_callback

    def publish_refcmd(self, command, target_team):
        """RefereeCmdメッセージをpublishする。"""
        msg = RefereeCmd()
        msg.command = command
        msg.target_team = target_team
        self._pub_refcmd.publish(msg)

    def _on_player_states(self, msg):
        """PlayerStates受信時の内部コールバック。"""
        if self._user_player_states_callback:
            self._user_player_states_callback(msg)

    # 必要に応じてサービスクライアント等も追加可能
