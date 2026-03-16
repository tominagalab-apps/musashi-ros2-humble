from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    refereebox_client_params_file = os.path.join(
        get_package_share_directory('musashi_rqt_refereebox_client'),
        'config',
        'refereebox_client_params.yaml'
    )

    gui_update_period_sec = LaunchConfiguration('gui_update_period_sec')
    player_states_send_period_sec = LaunchConfiguration('player_states_send_period_sec')
    
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

        # RefereeBoxClient を別ウィンドウで起動
        ExecuteProcess(
            cmd=[
                'rqt',
                '-s', 'musashi_rqt_refereebox_client.plugin.RefereeBoxClientPlugin',
                '--ros-args',
                '--params-file', refereebox_client_params_file,
                '-p', ['gui_update_period_sec:=', gui_update_period_sec],
                '-p', ['player_states_send_period_sec:=', player_states_send_period_sec],
            ],
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