# AGENTS.md

Guidance for future coding agents working in this ROS 2 workspace.

## Repository Shape

This is an AMR navigation workspace for Isaac Sim / Compal AMR experiments. Treat it as a ROS 2 colcon workspace rooted at this directory.

- `src/nav2`: `ament_python` package that installs Nav2 launch files, maps, RViz config, and Nav2 parameters.
- `src/pointcloud2scan`: `ament_python` package that launches `pointcloud_to_laserscan`.
- `src/dual_lidar_nav2`: `ament_python` package for a dual-lidar Nav2 setup, with its own map, RViz config, and Nav2 parameters.
- `src/explore`: `ament_cmake` package installed as `explore_lite`; implements a C++ frontier exploration node.
- `build/`, `install/`, and `log/`: generated colcon artifacts. Do not edit these by hand.

The source package name and folder name differ for exploration: the folder is `src/explore`, but the ROS package name is `explore_lite`.

## Build and Environment

Use a ROS 2 environment before building or running commands:

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build
source install/setup.bash
```

For scoped work, prefer package-selective builds:

```bash
colcon build --packages-select nav2 dual_lidar_nav2 pointcloud2scan explore_lite
colcon build --packages-select explore_lite
```

`src/explore/CMakeLists.txt` requires `ROS_DISTRO` to be defined and builds with C++14. It has conditional action naming for older distros (`dashing`, `eloquent`) and defaults to the modern `navigate_to_pose` action name otherwise.

## Launch Commands

Start navigation, including point cloud conversion, Nav2 bringup, and RViz:

```bash
source install/setup.bash
ros2 launch nav2 nav2_launch.py
```

Start the dual-lidar navigation setup:

```bash
source install/setup.bash
ros2 launch dual_lidar_nav2 nav2_launch.py
```

Start frontier exploration after SLAM and Nav2 are already running:

```bash
source install/setup.bash
ros2 launch explore_lite explore.launch.py
```

The main navigation launch file is `src/nav2/launch/nav2_launch.py`. It includes:

- `pointcloud2scan/launch/pointcloud2scan_launch.py`
- `nav2_bringup/launch/bringup_launch.py`
- `src/nav2/config/nav2_params_amp.yaml`
- `src/nav2/maps/my_test_map.yaml`
- `src/nav2/rviz2/nav2_setup.rviz`

The dual-lidar navigation launch file is `src/dual_lidar_nav2/launch/nav2_launch.py`. It includes:

- `pointcloud2scan/launch/dual_lidar_launch.py`
- `dual_laser_merger/dual_laser_merger_node`
- `nav2_bringup/launch/bringup_launch.py`
- `src/dual_lidar_nav2/config/nav2_params.yaml`
- `src/dual_lidar_nav2/maps/latest_map.yaml`
- `src/dual_lidar_nav2/rviz2/nav2_setup.rviz`

## Package Notes

### `nav2`

This package is mostly launch and data files. `setup.py` installs `launch/`, `config/`, `maps/`, and `rviz2/` into the package share directory. If you add new Nav2 assets, update `setup.py` only if they are outside those installed directories.

The default config uses simulated time and AMR-oriented Nav2 settings, including MPPI with an omni motion model. The laser scan topic is `scan`, supplied by `pointcloud2scan`.

### `dual_lidar_nav2`

This package is also mostly launch and data files, but it is for the dual-lidar pipeline. `setup.py` installs `launch/`, `config/`, `maps/`, and `rviz2/` into the package share directory.

The launch sequence starts two pointcloud-to-laserscan converters via `pointcloud2scan/launch/dual_lidar_launch.py`, then starts `dual_laser_merger_node`, Nav2 bringup, and RViz.

Important topics and frames:

- Front cloud input: `/front/point_cloud`
- Rear cloud input: `/rear/point_cloud`
- Front scan output: `/front/scan` with `target_frame: front_lidar`
- Rear scan output: `/rear/scan` with `target_frame: rear_lidar`
- Merged scan output: `/scan` with merger `target_frame: base_link`
- Nav2 AMCL scan topic: `/scan`
- Local costmap obstacle sources: `/front/scan` and `/rear/scan`
- Collision monitor source: `/scan`

The default map is `src/dual_lidar_nav2/maps/latest_map.yaml`. The Nav2 config uses a differential motion model, MPPI with `motion_model: "DiffDrive"`, simulated time, and an initial pose near `x: -6.505`, `y: 8.047`, `yaw: 3.14`.

There are ad hoc topic timestamp monitors in `src/dual_lidar_nav2/test/topic_check_v1.py` and `src/dual_lidar_nav2/test/topic_check_v2.py`. They are useful while the simulator and launch stack are running, but they are not installed as console scripts.

### `pointcloud2scan`

`src/pointcloud2scan/launch/pointcloud2scan_launch.py` launches `pointcloud_to_laserscan_node`.

Single-lidar defaults:

- Input remap: `cloud_in -> /point_cloud`
- Output remap: `scan -> /scan`
- `target_frame: rtx_lidar`
- `use_sim_time: True`

Dual-lidar defaults in `src/pointcloud2scan/launch/dual_lidar_launch.py`:

- `/front/point_cloud -> /front/scan`, `target_frame: front_lidar`
- `/rear/point_cloud -> /rear/scan`, `target_frame: rear_lidar`
- Common scan settings include full 360-degree angles, `angle_increment: 0.0087`, `scan_time: 0.0667`, `range_max: 20.0`, `use_inf: True`, and `use_sim_time: True`.
- A merged pointcloud-to-scan node for `/merged/point_cloud -> /scan` exists in comments only; the active merge path is `dual_laser_merger`.

Keep these aligned with Isaac Sim topic and TF names when changing sensor setup.

### `explore_lite`

The C++ executable is named `explore` and is installed under package `explore_lite`.

Core files:

- `src/explore/src/explore.cpp`: exploration node, Nav2 action client, resume/stop handling.
- `src/explore/src/frontier_search.cpp`: frontier detection and scoring.
- `src/explore/src/costmap_client.cpp`: occupancy grid / costmap access and TF handling.
- `src/explore/config/params.yaml`: default launch parameters.
- `src/explore/config/params_costmap.yaml`: alternate costmap-topic parameters.

The default launch loads `params.yaml`, remaps `/tf` and `/tf_static` to relative names for namespace support, and starts immediately. Runtime control is via `explore/resume` (`std_msgs/msg/Bool`).

## Tests and Checks

Run all tests after a full build:

```bash
colcon test
colcon test-result --verbose
```

Run package-specific tests when touching one package:

```bash
colcon test --packages-select explore_lite
colcon test --packages-select nav2 dual_lidar_nav2 pointcloud2scan
```

The Python packages use standard generated `ament_flake8`, `ament_pep257`, and copyright tests. The exploration package uses `ament_lint_auto` plus a small gtest in `src/explore/test/test_explore.cpp`.

## Development Conventions

- Keep source changes under `src/`; avoid editing generated files in `build/`, `install/`, or `log/`.
- Preserve ROS package names and installed share paths, especially `explore_lite` versus the `src/explore` directory name.
- Prefer changing launch/config defaults in source package files, then rebuilding and sourcing `install/setup.bash`.
- For Python launch files, keep the existing simple `generate_launch_description()` style.
- For C++ exploration code, keep C++14 compatibility unless the workspace baseline is deliberately raised.
- Do not remove existing license headers in the imported exploration code.
- Keep map, RViz, and parameter files installed through package setup/CMake install rules when adding new assets.

## Common Dependencies

This workspace expects ROS 2 plus:

- `nav2_bringup`
- `pointcloud_to_laserscan`
- `dual_laser_merger` for `dual_lidar_nav2`
- `rviz2`
- `slam_toolbox` for online mapping with exploration
- Nav2 messages/costmap packages used by `explore_lite`

If a build fails because a package cannot be found, verify the ROS distro is sourced and these dependencies are installed before changing source code.
