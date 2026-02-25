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
    pkg_nav2 = get_package_share_directory('nav2')

    # 2. 定義共用參數
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # 使用 os.path.join 組合路徑
    map_yaml_file = os.path.join(pkg_nav2, 'maps', 'my_test_map.yaml')
    # map_yaml_file = os.path.join(pkg_nav2, 'maps', 'csh_map.yaml')
    nav2_params_file = os.path.join(pkg_nav2, 'config', 'nav2_params_amp.yaml')
    rviz_config_file = os.path.join(pkg_nav2, 'rviz2', 'nav2_setup.rviz')

    # 3. 引入 pointcloud2scan
    pointcloud2scan_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('pointcloud2scan'), 
                         'launch', 'pointcloud2scan_launch.py')
        ]),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 4. 引入 Nav2 Bringup
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

    # 5. 啟動 RViz2
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
        pointcloud2scan_launch,
        nav2_launch,
        rviz_node
    ])