# bringup_launch.py
# rviz上に各プレイヤー状態を表示するためのlaunchファイル

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

colcon_ws_path = '/home/ubuntu/colcon_ws'
# colcon_ws_path = '/home/aviken/colcon_ws'


def generate_launch_description():

    team_spawn_launch_path = os.path.join(
        get_package_share_directory('musashi_rviz'),
        'launch',
        'team_spawn_launch.py'
    )

    return LaunchDescription([
        # ノードの起動
        # 1. musashi_rvizパッケージのnode_field_publisherを起動
        # rviz上にフィールドを描画する
        Node(
            package='musashi_rviz',
            executable='node_field_publisher',
        ),
        # 2. rviz2を起動
        # config.rvizを参照してレイアウトを読み込む
        # config.rvizは上書き保存して良い
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', colcon_ws_path + '/src/musashi-ros2-humble/basestation/musashi_rviz/rviz/config.rviz']
        ),
        # 3. team_spawn_launchを起動
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(team_spawn_launch_path),
        )
    ])
