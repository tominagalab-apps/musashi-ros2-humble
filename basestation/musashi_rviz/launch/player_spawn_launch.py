# player_spawn_launch.py
# playerのrobot_stateをパブリッシュするためのlaunchファイル

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

colcon_ws_path = '/home/ubuntu/colcon_ws'


def generate_launch_description():
  # 参照するURDFファイルへのパス
    urdf_file = get_package_share_directory(
        'musashi_description') + '/urdf/musashi_player.urdf'

    return LaunchDescription([

        # 本launchファイルのパラメータを定義
        # 各フレームのプレフィックス名
        DeclareLaunchArgument('frame_prefix', default_value=''),

        # 1. robot_state_publisherを起動
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': open(urdf_file).read(),
                'frame_prefix': LaunchConfiguration('frame_prefix'),
            }]
        ),
    ])
