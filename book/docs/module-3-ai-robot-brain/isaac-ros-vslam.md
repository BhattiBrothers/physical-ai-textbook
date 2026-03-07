---
sidebar_position: 3
---

# Isaac ROS & Visual SLAM (VSLAM)

Isaac ROS provides GPU-accelerated ROS 2 packages that run perception algorithms at real-time speeds on NVIDIA hardware. This lesson focuses on Visual SLAM for robot localization and Nav2 integration for autonomous navigation.

## What is Isaac ROS?

Isaac ROS is a collection of hardware-accelerated ROS 2 packages optimized for NVIDIA GPUs and Jetson edge AI platforms. It provides:

- **GPU-accelerated image processing** — 10-100x faster than CPU implementations
- **VSLAM** — Real-time visual odometry and mapping
- **Object detection** — Optimized YOLO, PeopleNet, and custom models via Triton
- **Depth estimation** — Stereo and monocular depth perception
- **Pose estimation** — 6-DoF object pose for manipulation

## Setting Up Isaac ROS

### Prerequisites

```bash
# Ubuntu 22.04 + ROS 2 Humble required
# NVIDIA GPU with CUDA 11.8+ OR Jetson (Orin series recommended)

# Install Isaac ROS common packages
sudo apt update
sudo apt install ros-humble-isaac-ros-common

# Set up Isaac ROS workspace
mkdir -p ~/workspaces/isaac_ros-dev/src
cd ~/workspaces/isaac_ros-dev/src
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox.git

cd ~/workspaces/isaac_ros-dev
colcon build --symlink-install
source install/setup.bash
```

### Docker-Based Setup (Recommended)

```bash
# Use the Isaac ROS Docker container for consistent environment
cd ~/workspaces/isaac_ros-dev/src/isaac_ros_common
./scripts/run_dev.sh ~/workspaces/isaac_ros-dev

# Inside Docker container:
cd /workspaces/isaac_ros-dev
colcon build --symlink-install --packages-up-to isaac_ros_visual_slam
source install/setup.bash
```

## Visual SLAM with Isaac ROS

VSLAM estimates the robot's position and builds a 3D map of the environment using only camera input — no GPS required.

### Launching VSLAM

```bash
# With RealSense D435 camera
ros2 launch realsense2_camera rs_launch.py \
  depth_module.depth_profile:=640x480x30 \
  rgb_camera.color_profile:=640x480x30 \
  enable_gyro:=true enable_accel:=true \
  unite_imu_method:=1

# In a second terminal — launch VSLAM
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam_realsense.launch.py
```

### VSLAM ROS 2 Nodes

```python
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Image, Imu
import numpy as np

class VSLAMMonitor(Node):
    """Monitor VSLAM output and republish for Nav2."""

    def __init__(self):
        super().__init__('vslam_monitor')

        # Subscribe to VSLAM pose output
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/visual_slam/tracking/odometry',
            self.pose_callback,
            10
        )

        # Subscribe to VSLAM odometry
        self.odom_sub = self.create_subscription(
            Odometry,
            '/visual_slam/tracking/slam_path',
            self.odom_callback,
            10
        )

        # Publish clean odometry for Nav2
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        self.get_logger().info('VSLAM Monitor started')
        self._last_pose = None

    def pose_callback(self, msg: PoseStamped):
        self._last_pose = msg
        self.get_logger().debug(
            f'Position: ({msg.pose.position.x:.3f}, '
            f'{msg.pose.position.y:.3f}, '
            f'{msg.pose.position.z:.3f})'
        )

    def odom_callback(self, msg: Odometry):
        # Forward to Nav2 odom topic
        self.odom_pub.publish(msg)

def main():
    rclpy.init()
    node = VSLAMMonitor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Understanding the VSLAM Pipeline

```
Stereo/RGB-D Camera
       │
       ▼
Image Rectification (GPU)
       │
       ▼
Feature Extraction (GPU - ORB/SIFT)
       │
       ▼
Feature Matching across frames
       │
       ▼
Motion Estimation (PnP solver)
       │
       ├──────────────────────────────────┐
       ▼                                  ▼
  Visual Odometry                   Loop Closure Detection
  (relative motion)                 (recognize visited places)
       │                                  │
       └──────────────┬───────────────────┘
                      ▼
              Graph Optimization (g2o)
                      │
                      ▼
              Global Map + Robot Pose
```

## Navigation with Nav2

### Nav2 Configuration for Humanoid

```yaml
# nav2_params_humanoid.yaml
amcl:
  ros__parameters:
    use_sim_time: true
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_link"
    beam_skip_distance: 0.5
    global_frame_id: "map"
    laser_model_type: "likelihood_field"
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    update_min_a: 0.2
    update_min_d: 0.25

bt_navigator:
  ros__parameters:
    use_sim_time: true
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    default_bt_xml_filename: "navigate_w_replanning_and_recovery.xml"

controller_server:
  ros__parameters:
    use_sim_time: true
    controller_frequency: 20.0
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]

    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: true
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.26
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.26
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
```

### Sending Navigation Goals Programmatically

```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import math

class HumanoidNavigator(Node):
    """High-level navigation interface for humanoid robot."""

    def __init__(self):
        super().__init__('humanoid_navigator')
        self._nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info('Navigator ready')

    def navigate_to(self, x: float, y: float, yaw: float = 0.0):
        """Send robot to (x, y) with given heading."""
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.position.z = 0.0

        # Convert yaw to quaternion
        goal.pose.pose.orientation.z = math.sin(yaw / 2)
        goal.pose.pose.orientation.w = math.cos(yaw / 2)

        self.get_logger().info(f'Navigating to ({x:.2f}, {y:.2f}), yaw={math.degrees(yaw):.1f}°')

        self._nav_client.wait_for_server()
        future = self._nav_client.send_goal_async(
            goal,
            feedback_callback=self._feedback_callback
        )
        future.add_done_callback(self._goal_response_callback)

    def _feedback_callback(self, feedback_msg):
        dist = feedback_msg.feedback.distance_remaining
        self.get_logger().info(f'Distance remaining: {dist:.2f} m')

    def _goal_response_callback(self, future):
        result = future.result()
        if result.accepted:
            self.get_logger().info('Goal accepted!')
        else:
            self.get_logger().warn('Goal rejected!')

def main():
    rclpy.init()
    navigator = HumanoidNavigator()

    # Navigate to waypoints
    waypoints = [(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
    for x, y in waypoints:
        navigator.navigate_to(x, y)

    rclpy.spin(navigator)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Nvblox: 3D Scene Reconstruction

Isaac ROS Nvblox builds real-time 3D voxel maps from depth images, enabling collision-aware navigation.

```bash
# Launch Nvblox with RealSense
ros2 launch nvblox_examples_bringup realsense_example.launch.py

# Visualize in RViz2
ros2 launch nvblox_examples_bringup visualization.launch.py
```

```python
# Subscribe to Nvblox occupancy map for planning
from nav_msgs.msg import OccupancyGrid

class NvbloxMapSubscriber(Node):
    def __init__(self):
        super().__init__('map_subscriber')
        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/nvblox_node/static_map_slice',
            self.map_callback,
            10
        )

    def map_callback(self, msg: OccupancyGrid):
        width = msg.info.width
        height = msg.info.height
        resolution = msg.info.resolution
        self.get_logger().info(
            f'Map: {width}x{height} cells @ {resolution:.3f} m/cell'
        )
```

## Exercises

1. Launch Isaac ROS VSLAM with a RealSense camera (or ROS bag) and visualize the trajectory in RViz2
2. Configure Nav2 to navigate a differential-drive robot through a 3-waypoint course
3. Compare CPU vs GPU performance of VSLAM by profiling with `ros2 run rqt_top rqt_top`
4. Build an Nvblox 3D map of a room and use it for collision-free path planning

## Summary

| Tool | Purpose | Key Benefit |
|------|---------|-------------|
| Isaac ROS VSLAM | Localization without GPS | GPU-accelerated, runs on Jetson |
| Nav2 | Path planning & control | Mature, humanoid-configurable |
| Nvblox | Real-time 3D mapping | Collision-aware navigation |
