#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf2_ros
import time
import math

class Tf2Sample01(Node):
    def __init__(self):
        super().__init__('tf2_sample01')
        
        self.yaw = 0.0
        
        # Transform Broadcasterの初期化
        self.br = tf2_ros.TransformBroadcaster(self)
        
        # タイマコールバック関数の作成
        self.timer = self.create_timer(0.1, self.timer_callback)
        
    def timer_callback(self,):
        self.get_logger().info('callback')
      
        # 現在時刻の取得
        now = self.get_clock().now().to_msg()
        
        # TransformStampedメッセージの作成
        t = TransformStamped()

        t.header.stamp = now
        t.header.frame_id = 'map' # ワールド座標系の名前
        t.child_frame_id = 'base_link' # ロボット座標系の名前
        
        # トランスフォームの設定
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        # 回転の設定 (yaw = 90度)
        self.yaw = self.yaw + 0.1
        quat = self.euler_to_quaternion(0, 0, self.yaw)
        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]
        
         # ブロードキャスト
        self.br.sendTransform(t)
        
    def euler_to_quaternion(self, roll, pitch, yaw):
        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        return [qx, qy, qz, qw]

def main(args=None):
    rclpy.init(args=args)
    node = Tf2Sample01()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
