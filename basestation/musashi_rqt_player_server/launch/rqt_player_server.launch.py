def generate_launch_description():
    from launch import LaunchDescription
    from launch.actions import ExecuteProcess

    return LaunchDescription([
        ExecuteProcess(
            cmd=['rqt', '--standalone', 'musashi_rqt_player_server'],
            output='screen',
        ),
    ])
