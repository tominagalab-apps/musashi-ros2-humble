def generate_launch_description():
    from ament_index_python.packages import get_package_share_directory
    from launch import LaunchDescription
    from launch.actions import DeclareLaunchArgument, ExecuteProcess
    from launch.substitutions import LaunchConfiguration
    import os

    default_params_file = os.path.join(
        get_package_share_directory('musashi_rqt_refereebox_client'),
        'config',
        'refereebox_client_params.yaml',
    )
    params_file = LaunchConfiguration('params_file')
    gui_update_period_sec = LaunchConfiguration('gui_update_period_sec')
    player_states_send_period_sec = LaunchConfiguration(
        'player_states_send_period_sec'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file,
            description='ROS parameter file for musashi_rqt_refereebox_client',
        ),
        DeclareLaunchArgument(
            'gui_update_period_sec',
            default_value='0.033',
            description='GUI update period for RefereeBoxClient [sec]',
        ),
        DeclareLaunchArgument(
            'player_states_send_period_sec',
            default_value='0.25',
            description='player_states send period to RefereeBox [sec]',
        ),
        ExecuteProcess(
            cmd=[
                'rqt',
                '--standalone',
                'musashi_rqt_refereebox_client',
                '--ros-args',
                '--params-file',
                params_file,
                '-p',
                ['gui_update_period_sec:=', gui_update_period_sec],
                '-p',
                [
                    'player_states_send_period_sec:=',
                    player_states_send_period_sec,
                ],
            ],
            output='screen',
        ),
    ])
