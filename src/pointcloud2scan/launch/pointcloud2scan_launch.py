from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan',
            remappings=[
                # 將輸入 topic 改為你的 Isaac Sim 發布的 topic
                ('cloud_in', '/point_cloud'),
                # 輸出 topic 改為 Nav2 預設接收的 /scan
                ('scan', '/scan'),
            ],
            parameters=[{
                'target_frame': 'rtx_lidar', # 轉換後的座標系，通常是機器人底盤中心
                'transform_tolerance': 0.01,
                'min_height': 0.1,            # 點雲投影的最小高度 (米)
                'max_height': 1.0,            # 點雲投影的最大高度 (米)
                'angle_min': -3.14159,        # -180 度
                'angle_max': 3.14159,         # 180 度
                'angle_increment': 0.0087,    # 角度解析度 (約 0.5 度)
                'scan_time': 0.3333,
                'range_min': 0.4,            # 忽略太靠近機器人本體的點
                'range_max': 10.0,            # 最大偵測距離
                'use_inf': True,
                'inf_epsilon': 1.0,
                'use_sim_time': True,         # 務必設為 True 以同步 Isaac Sim 時間
            }],
        )
    ])