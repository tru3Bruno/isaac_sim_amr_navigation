# AMR Navigation Workspace

This is a ROS2 navigation and exploration workspace, mainly used for AMR navigation (Nav2) and frontier-based exploration in isaac-sim with Compal AMR.

<div align="center"><a class="reference internal image-reference" href="https://raw.githubusercontent.com/tru3Bruno/isaac_sim_amr_navigation/main/images/amr_nav.gif/"><img alt="image" src="https://raw.githubusercontent.com/tru3Bruno/isaac_sim_amr_navigation/main/images/amr_nav.gif/" width="800px"/></a></div>

There are 3 main packages under `src/`:
- `nav2`: Integrates Nav2 bringup, maps, RViz, and navigation parameters.
- `pointcloud2scan`: Converts `/point_cloud` to `/scan` using `pointcloud_to_laserscan`.
- `explore_lite` (folder name `explore`): A C++ node for frontier-based autonomous exploration.

## Workspace Structure

```text
ros2_ws/
├── src/
│   ├── nav2/
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

Main file:
- `src/pointcloud2scan/launch/pointcloud2scan_launch.py`

Key points:
- Subscribes to `cloud_in -> /point_cloud`
- Publishes `scan -> /scan`
- Uses `target_frame: rtx_lidar`

This package allows Nav2 costmaps to consume `LaserScan` data directly.

### 3) explore_lite package

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
colcon build
source install/setup.bash
```

## Launch

### A. Start navigation (pointcloud2scan + Nav2 + RViz)

```bash
source install/setup.bash
ros2 launch nav2 nav2_launch.py
```

### B. Start frontier exploration (requires a working map and Nav2 first)

```bash
source install/setup.bash
ros2 launch explore_lite explore.launch.py
```

## Dependencies (minimum)

- ROS 2 (matching your OS / distro)
- Nav2 (including `nav2_bringup`)
- `pointcloud_to_laserscan`
- RViz2
- `slam_toolbox` (if you need online mapping)

## References
- [ROS2 Explore Lite](https://github.com/robo-friends/m-explore-ros2)
