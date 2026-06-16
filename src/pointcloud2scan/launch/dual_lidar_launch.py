from launch import LaunchDescription
from launch_ros.actions import Node


def make_pointcloud_to_scan_node(
    name,
    cloud_topic,
    scan_topic,
    params,
):
    return Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name=name,
        output='screen',
        remappings=[
            ('cloud_in', cloud_topic),
            ('scan', scan_topic),
        ],
        parameters=[params],
    )


def generate_launch_description():

    common_params = {
        # 'target_frame': 'base_link',
        'transform_tolerance': 0.05,
        'angle_min': -3.14159,
        'angle_max': 3.14159,
        'angle_increment': 0.0087,
        'use_inf': True,
        'inf_epsilon': 1.0,
        'use_sim_time': True,
    }

    front_params = {
        **common_params,
        'target_frame': 'front_lidar',
        'min_height': -0.1,
        'max_height': 0.5,
        'scan_time': 0.0667,   # 15 Hz
        'range_min': 0.1,
        'range_max': 20.0,
    }

    rear_params = {
        **common_params,
        'target_frame': 'rear_lidar',
        'min_height': -0.1,
        'max_height': 1.5,
        'scan_time': 0.0667,
        'range_min': 0.1,
        'range_max': 20.0,
    }

    merged_params = {
        **common_params,
        'target_frame': 'base_link',
        'min_height': 0.1,
        'max_height': 2.0,
        'scan_time': 0.0667,
        'range_min': 0.2,
        'range_max': 20.0,
    }

    return LaunchDescription([
        make_pointcloud_to_scan_node(
            name='front_pointcloud_to_laserscan',
            cloud_topic='/front/point_cloud',
            scan_topic='/front/scan',
            params=front_params,
        ),

        make_pointcloud_to_scan_node(
            name='rear_pointcloud_to_laserscan',
            cloud_topic='/rear/point_cloud',
            scan_topic='/rear/scan',
            params=rear_params,
        ),

        #make_pointcloud_to_scan_node(
        #    name='merged_pointcloud_to_laserscan',
        #    cloud_topic='/merged/point_cloud',
        #    scan_topic='/scan',
        #    params=merged_params,
        #),
    ])