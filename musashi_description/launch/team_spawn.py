# launch/display.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace
from ament_index_python.packages import get_package_share_directory
import os

p1_name = 'player1'
p2_name = 'player2'
p3_name = 'player3'
p4_name = 'player4'
p5_name = 'player5'

def generate_launch_description():

    player_spawn_launch_path = os.path.join(
        get_package_share_directory('musashi_description'),
        'launch',
        'player_spawn.py'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'p1_frame_prefix',
            default_value=p1_name + '/',
        ),
        DeclareLaunchArgument(
            'p2_frame_prefix',
            default_value=p2_name + '/',
        ),
        DeclareLaunchArgument(
            'p3_frame_prefix',
            default_value=p3_name + '/',
        ),
        DeclareLaunchArgument(
            'p4_frame_prefix',
            default_value=p4_name + '/',
        ),
        DeclareLaunchArgument(
            'p5_frame_prefix',
            default_value=p5_name + '/',
        ),

        GroupAction([
            PushRosNamespace(p1_name),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(player_spawn_launch_path),
                launch_arguments={
                    'frame_prefix': LaunchConfiguration('p1_frame_prefix')}.items()
            ),
        ]),

        GroupAction([
            PushRosNamespace(p2_name),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(player_spawn_launch_path),
                launch_arguments={
                    'frame_prefix': LaunchConfiguration('p2_frame_prefix')}.items()
            ),
        ]),
        GroupAction([
            PushRosNamespace(p3_name),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(player_spawn_launch_path),
                launch_arguments={
                    'frame_prefix': LaunchConfiguration('p3_frame_prefix')}.items()
            ),
        ]),
        GroupAction([
            PushRosNamespace(p4_name),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(player_spawn_launch_path),
                launch_arguments={
                    'frame_prefix': LaunchConfiguration('p4_frame_prefix')}.items()
            ),
        ]),
        GroupAction([
            PushRosNamespace(p5_name),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(player_spawn_launch_path),
                launch_arguments={
                    'frame_prefix': LaunchConfiguration('p5_frame_prefix')}.items()
            ),
        ]),
    ])
