import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name='e_robot' #<--- CHANGE ME
    rviz_dir = os.path.join(get_package_share_directory(package_name),'config','view_e-bot_navigation.rviz')
    slam_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'mapper_params_online_async.yaml')
    gazebo_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'gazebo_params.yaml')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name),'launch','rsp.launch.py')]), 
            launch_arguments={'use_sim_time': 'true', 'use_ros2_control' : 'true', 'use_rgbd_camera' : 'true'}.items())

    start_gazebo_server = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory("gazebo_ros"), "launch", "gzserver.launch.py"
    )))

    start_gazebo_client = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory("gazebo_ros"), "launch", "gzclient.launch.py"
    )))
    
    joystick = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'joystick.launch.py')]))
    
    mapping = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')]),
            launch_arguments={'slam_params_file': slam_params_file,
            'use_sim_time': 'true'}.items())

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
        arguments=['-topic', 'robot_description','-entity', 'e_robot'],
        output='screen')
    
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"])

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"])
    
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_node',
        arguments=['-d', rviz_dir],
        output='screen')

    # Launch them all!
    return LaunchDescription([
        rsp,
        rviz,
        start_gazebo_server,
        start_gazebo_client,
        mapping,
        joystick,
        spawn_entity,
        diff_drive_spawner,
        joint_broad_spawner
    ])