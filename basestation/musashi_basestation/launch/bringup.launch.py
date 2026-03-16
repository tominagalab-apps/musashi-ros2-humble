from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    gui_update_period_sec = LaunchConfiguration('gui_update_period_sec')
    player_states_send_period_sec = LaunchConfiguration(
        'player_states_send_period_sec'
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'gui_update_period_sec',
            default_value='0.033',
            description='GUI update period for RefereeBoxClient [sec]'
        ),
        DeclareLaunchArgument(
            'player_states_send_period_sec',
            default_value='0.25',
            description='player_states send period to RefereeBox [sec]'
        ),

        # RefereeBoxClient は専用 launch を利用して起動
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('musashi_rqt_refereebox_client'),
                    'launch',
                    'rqt_refereebox_client.launch.py',
                )
            ),
            launch_arguments={
                'gui_update_period_sec': gui_update_period_sec,
                'player_states_send_period_sec': player_states_send_period_sec,
            }.items(),
        ),

        # PlayerServer は専用 launch を利用して起動
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('musashi_rqt_player_server'),
                    'launch',
                    'rqt_player_server.launch.py',
                )
            )
        ),

        # PlayerController は専用 launch を利用して起動
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('musashi_rqt_player_controller'),
                    'launch',
                    'rqt_player_controller.launch.py',
                )
            )
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