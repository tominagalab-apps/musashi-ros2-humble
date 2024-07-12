# player_spawn_launch.py
# team全員ををパブリッシュするためのlaunchファイル

from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace
from ament_index_python.packages import get_package_share_directory
import os

colcon_ws_path = '/home/ubuntu/colcon_ws'

PLAYER_NUM = 5


def generate_launch_description():
    player_spawn_launch_path = os.path.join(
        get_package_share_directory('musashi_rviz'),
        'launch',
        'player_spawn_launch.py'
    )

    groups = []
    for i in range(PLAYER_NUM): # プレイヤー数分の繰り返し処理
        groups.append(
            GroupAction([
                PushRosNamespace('player' + str(i + 1)), # プレイヤー名'player*'で名前空間を作成
                IncludeLaunchDescription( # player_spawn_launch.pyをパラメータを渡しながら実行する
                    PythonLaunchDescriptionSource(player_spawn_launch_path),
                    launch_arguments=[
                        ('frame_prefix', 'player' + str(i + 1) + '/'),
                    ]
                ),
            ])
        )

    return LaunchDescription([
        groups[0],
        groups[1],
        groups[2],
        groups[3],
        groups[4],
    ])
