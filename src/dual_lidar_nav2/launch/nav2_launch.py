import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. 取得 Package 的路徑 (不再寫死 /home/omniverse/...)
    # 這裡假設你的 package 名稱是 nav2
    pkg_nav2 = get_package_share_directory('dual_lidar_nav2')

    # 2. 定義共用參數
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # 使用 os.path.join 組合路徑
    map_yaml_file = os.path.join(pkg_nav2, 'maps', 'latest_map.yaml')
    nav2_params_file = os.path.join(pkg_nav2, 'config', 'nav2_params.yaml')
    rviz_config_file = os.path.join(pkg_nav2, 'rviz2', 'nav2_setup.rviz')

    # 3. 引入 lidar_merge
    #dual_lidar_merge_node = Node(
    #    package='dual_lidar_merge',
    #    executable='pointcloud_merge_node',
    #    name='dual_lidar_pointcloud_merger',
    #    output='screen',
    #    parameters=[
    #        {
    #            'use_sim_time': use_sim_time,
    #            'target_frame': 'base_link',
    #            'front_topic': '/front/point_cloud',
    #            'rear_topic': '/rear/point_cloud',
    #            'output_topic': '/merged/point_cloud',
    #            'queue_size': 10,
    #            'slop': 0.1,
    #            'use_latest_tf': True,
    #        }
    #    ]
    #)

    # 3. 引入 lidar_merge
    dual_laser_merger_node = Node(
        package='dual_laser_merger',
        executable='dual_laser_merger_node',
        name='dual_laser_merger_node',
        output='screen',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'laser_1_topic': '/front/scan',
                'laser_2_topic': '/rear/scan',
                'merged_scan_topic': '/scan',
                'publish_rate': 67,
                'target_frame': 'base_link',
                'angle_min': -3.141592654,
                'angle_max': 3.141592654,
                'angle_increment': 0.008726646,
                'scan_time': 0.0667,
                'range_min': 0.1,
                'range_max': 20.0,
                'min_height': -0.5,
                'max_height': 0.5,
                'use_inf': True,
            }
        ]
    )

    # 4. 引入 p2s
    pointcloud2scan_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('pointcloud2scan'), 
                         'launch', 'dual_lidar_launch.py')
        ]),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 5. 引入 Nav2 Bringup
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('nav2_bringup'), 
                         'launch', 'bringup_launch.py')
        ]),
        launch_arguments={
            'map': map_yaml_file,
            'params_file': nav2_params_file,
            'use_sim_time': use_sim_time
        }.items()
    )

    # 6. 啟動 RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        #dual_lidar_merge_node,
        pointcloud2scan_launch,
        dual_laser_merger_node,
        nav2_launch,
        rviz_node
    ])