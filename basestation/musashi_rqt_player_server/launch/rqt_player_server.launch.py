def generate_launch_description():
    from ament_index_python.packages import get_package_share_directory
    from launch import LaunchDescription
    from launch.actions import DeclareLaunchArgument, ExecuteProcess
    from launch.substitutions import LaunchConfiguration
    import os

    default_params_file = os.path.join(
        get_package_share_directory('musashi_rqt_player_server'),
        'config',
        'player_server_params.yaml',
    )
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file,
            description='ROS parameter file for musashi_rqt_player_server',
        ),
        ExecuteProcess(
            cmd=[
                'rqt',
                '--standalone',
                'musashi_rqt_player_server',
                '--ros-args',
                '--params-file',
                params_file,
            ],
            output='screen',
        ),
    ])
