#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

datum_lat = 13.763656
datum_lon = 100.527998

def generate_launch_description():
    pkg_share = get_package_share_directory('transporter_localization')
    
    # EKF node for sensor fusion
    ekf_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_odom',
        output='screen',
        parameters=[os.path.join(pkg_share, 'config/localization_sim.yaml')],
        remappings=[
            ('/odometry/filtered', '/odom'),
            # Remove the IMU remapping since URDF publishes to /imu/data directly
        ]
    )
    
    # NavSat Transform node to convert GPS to local coordinates
    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        output='screen',
        parameters=[os.path.join(pkg_share, 'config/localization_sim.yaml')],
        remappings=[
            ('/gps/fix', '/gps/fix'),    # GPS fix data
            ('/odometry/filtered', '/odom'),  # EKF output for heading
            ('/odometry/gps', '/odometry/gps'),  # Output GPS odometry
        ]
    )
    
    # Static transform from world to map (if needed for visualization)
    # This is optional and only for aligning coordinate systems
    world_to_map_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='world_to_map_tf',
        output='screen',
        # No rotation needed if both use same convention
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )
    
    return LaunchDescription([
        ekf_localization_node,
        navsat_transform_node,
        world_to_map_tf,  # Optional
    ])