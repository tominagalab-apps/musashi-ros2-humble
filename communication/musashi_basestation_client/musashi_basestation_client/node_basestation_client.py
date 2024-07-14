#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from musashi_msgs.msg import PlayerState

from musashi_basestation_client.basestation_client import BaseStationClient

class BasestationClientNode(Node):
    def __init__(self):
        super().__init__('node_basestation_client')
        
        # インスタンス作成
        basestation_client = BaseStationClient()
        
        # スレッドのスタート
        basestation_client.start()
        
        # サブスクライバー作成
        self._sub_player_state = self.create_subscription(
            PlayerState,
            '/player_state',
            self.player_state_callback,
            10,
        )
        
    def player_state_callback(self):
        return


def main(args=None):
    rclpy.init(args=args)
    node = BasestationClientNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
