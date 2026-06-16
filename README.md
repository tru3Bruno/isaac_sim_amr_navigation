# AMR Navigation Workspace

This is a ROS2 navigation and exploration workspace, mainly used for AMR navigation (Nav2) and frontier-based exploration in isaac-sim with Compal AMR (.usd is not included).

<div align="center"><a class="reference internal image-reference" href="https://raw.githubusercontent.com/tru3Bruno/isaac_sim_amr_navigation/main/images/amr_nav.gif"><img alt="image" src="https://raw.githubusercontent.com/tru3Bruno/isaac_sim_amr_navigation/main/images/amr_nav.gif" width="800px"/></a></div>

There are 4 main packages under `src/`:
- `nav2`: Integrates Nav2 bringup, maps, RViz, and navigation parameters.
- `pointcloud2scan`: Converts `/point_cloud` to `/scan` using `pointcloud_to_laserscan`.
- `dual_lidar_nav2`: A dual-lidar Nav2 setup with its own launch file, map, RViz config, and navigation parameters.
- `explore_lite` (folder name `explore`): A C++ node for frontier-based autonomous exploration.

## Workspace Structure

```text
ros2_ws/
├── src/
│   ├── nav2/
│   ├── dual_lidar_nav2/
│   ├── pointcloud2scan/
│   └── explore/
├── build/
├── install/
└── log/
```

- `build/`, `install/`, and `log/` are colcon build/runtime artifacts.
- The maintainable source code is mainly under `src/`.

## Feature Overview

### 1) nav2 package

Main files:
- `src/nav2/launch/nav2_launch.py`
- `src/nav2/config/nav2_params_amp.yaml`
- `src/nav2/maps/my_test_map.yaml`
- `src/nav2/rviz2/nav2_setup.rviz`

`nav2_launch.py` does the following:
1. Includes the `pointcloud2scan` launch (converts point cloud to laser scan first).
2. Includes `nav2_bringup/bringup_launch.py`.
3. Applies map and Nav2 parameters (defaults to `nav2_params_amp.yaml`).
4. Starts RViz2.

### 2) pointcloud2scan package

Main files:
- `src/pointcloud2scan/launch/pointcloud2scan_launch.py`
- `src/pointcloud2scan/launch/dual_lidar_launch.py`

Key points:
- Single-lidar launch subscribes to `cloud_in -> /point_cloud`
- Single-lidar launch publishes `scan -> /scan`
- Single-lidar launch uses `target_frame: rtx_lidar`
- Dual-lidar launch converts:
  - `/front/point_cloud -> /front/scan` with `target_frame: front_lidar`
  - `/rear/point_cloud -> /rear/scan` with `target_frame: rear_lidar`

This package allows Nav2 costmaps to consume `LaserScan` data directly.

### 3) dual_lidar_nav2 package

Main files:
- `src/dual_lidar_nav2/launch/nav2_launch.py`
- `src/dual_lidar_nav2/config/nav2_params.yaml`
- `src/dual_lidar_nav2/maps/latest_map.yaml`
- `src/dual_lidar_nav2/rviz2/nav2_setup.rviz`

`dual_lidar_nav2/launch/nav2_launch.py` does the following:
1. Includes `pointcloud2scan/launch/dual_lidar_launch.py` to convert front and rear point clouds into LaserScan topics.
2. Starts `dual_laser_merger_node` to merge `/front/scan` and `/rear/scan` into `/scan`.
3. Includes `nav2_bringup/bringup_launch.py`.
4. Applies the dual-lidar map and Nav2 parameters.
5. Starts RViz2.

Key topics:
- Input point clouds: `/front/point_cloud`, `/rear/point_cloud`
- Per-lidar scans: `/front/scan`, `/rear/scan`
- Merged scan for AMCL / collision monitor: `/scan`
- Local costmap obstacle sources: `/front/scan`, `/rear/scan`

### 4) explore_lite package

Main files:
- `src/explore/launch/explore.launch.py`
- `src/explore/src/explore.cpp`
- `src/explore/src/frontier_search.cpp`
- `src/explore/config/params.yaml`

Key points:
- Subscribes to OccupancyGrid and update messages, then searches frontiers.
- Sends navigation goals through the `NavigateToPose` action.
- Supports unreachable-frontier blacklisting and `explore/resume` control.

## Build

Run in the workspace root:

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build
source install/setup.bash
```

## Launch

### A. Start navigation (pointcloud2scan + Nav2 + RViz)

```bash
source install/setup.bash
ros2 launch nav2 nav2_launch.py
```

### B. Start dual-lidar navigation (front/rear lidar + merge + Nav2 + RViz)

```bash
source install/setup.bash
ros2 launch dual_lidar_nav2 nav2_launch.py
```

### C. Start frontier exploration (requires SLAM and Nav2 first)

```bash
source install/setup.bash
ros2 launch explore_lite explore.launch.py
```

## Dependencies (minimum)

- ROS 2 (matching your OS / distro)
- Nav2 (including `nav2_bringup`)
- `pointcloud_to_laserscan`
- `dual_laser_merger` (for `dual_lidar_nav2`)
- RViz2
- `slam_toolbox` (online mapping with frontier exploration)

## References
- [ROS2 Explore Lite](https://github.com/robo-friends/m-explore-ros2)
