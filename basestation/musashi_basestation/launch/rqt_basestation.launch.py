from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    
    return LaunchDescription([
        # RefereeBoxClient を別ウィンドウで起動
        ExecuteProcess(
            cmd=['rqt', '-s', 'musashi_rqt_refereebox_client.rqt_refereebox_plugin.RqtRefereeBoxClient'],
            output='screen'
        ),

        # PlayerServer を別ウィンドウで起動
        ExecuteProcess(
           cmd=['rqt', '-s', 'musashi_rqt_player_server.rqt_player_server.RqtPlayerServer'],
           output='screen'
       ), 
       
       # PlayerController を別ウィンドウで起動
        ExecuteProcess(
           cmd=['rqt', '-s', 'musashi_rqt_player_controller.rqt_player_controller.RqtPlayerController'],
           output='screen'
       ),
        
        # フィールド，プレイヤー可視化用rvizの起動
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('musashi_rviz'),
                    'launch',
                    'bringup_launch.py'
                )
            )
        )
    ])