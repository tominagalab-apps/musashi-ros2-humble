from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # rqt設定ファイルのパス
    cfg_path = os.path.join(
        get_package_share_directory('musashi_basestation'),
        'config',
        'rqt_basestation_plugins.rqt'
    )

    # musashi_rvizのbringup_launch.pyのパス
    rviz_bringup_launch_path = os.path.join(
        get_package_share_directory('musashi_rviz'),
        'launch',
        'bringup_launch.py'
    )

    return LaunchDescription([
        # RViz (フィールド可視化) を起動
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rviz_bringup_launch_path)
        ),

        # rqt (コマンド・監視) を起動
        ExecuteProcess(
            cmd=['rqt', '--load-config', cfg_path],
            output='screen'
        )
    ])