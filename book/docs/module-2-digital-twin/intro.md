---
sidebar_position: 1
---

# The Digital Twin: Gazebo & Unity

A **digital twin** is a virtual representation of a physical system that mirrors its behavior in real-time. In this module, you'll learn to create digital twins of humanoid robots using Gazebo for physics simulation and Unity for high-fidelity visualization.

## Why Digital Twins Matter

Digital twins enable:
- **Safe Testing**: Test control algorithms without risk to hardware
- **Rapid Prototyping**: Iterate designs quickly in simulation
- **Sim-to-Real Transfer**: Train AI models in simulation and deploy to real robots
- **Predictive Maintenance**: Monitor virtual sensors to predict failures

## Module Learning Objectives

By the end of this module, you will be able to:
1. Set up Gazebo simulation environments for humanoid robots
2. Create URDF and SDF robot description files
3. Simulate physics, gravity, and collisions in Gazebo
4. Implement sensor simulation (LiDAR, cameras, IMUs)
5. Create high-fidelity visualizations in Unity
6. Build human-robot interaction scenarios

## Tools and Technologies

### Gazebo
- **Purpose**: Physics simulation and sensor emulation
- **Key Features**: Realistic physics engines (ODE, Bullet), sensor models, plugin system
- **Integration**: Native ROS 2 support via `ros_gz_bridge`

### Unity
- **Purpose**: High-fidelity rendering and interactive environments
- **Key Features**: Photorealistic graphics, VR/AR support, asset store
- **Integration**: ROS 2 connectivity via ROS# or ROS-TCP-Connector

### NVIDIA Isaac Sim (Preview)
- **Purpose**: Photorealistic simulation and synthetic data generation
- **Key Features**: RTX-accelerated rendering, domain randomization
- **Integration**: Part of NVIDIA Omniverse ecosystem

## Weekly Breakdown

### Week 6-7: Robot Simulation with Gazebo
- Gazebo simulation environment setup
- URDF and SDF robot description formats
- Physics simulation and sensor simulation
- Introduction to Unity for robot visualization

## URDF vs SDF

### URDF (Unified Robot Description Format)
- **Purpose**: Describe robot kinematics and visual properties
- **Strengths**: Simple XML format, ROS-native, good for basic descriptions
- **Limitations**: No direct simulation capabilities, limited physics properties

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder length="0.6" radius="0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.6" radius="0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10"/>
      <inertia ixx="0.4" ixy="0" ixz="0" iyy="0.4" iyz="0" izz="0.2"/>
    </inertial>
  </link>
</robot>
```

### SDF (Simulation Description Format)
- **Purpose**: Comprehensive simulation description including physics, sensors, lights
- **Strengths**: More features than URDF, Gazebo-native, better for complex simulations
- **Limitations**: More complex, less ROS integration

## Setting Up Gazebo with ROS 2

```bash
# Install Gazebo with ROS 2 integration
sudo apt install ros-humble-gazebo-ros-pkgs

# Launch an empty Gazebo world
ros2 launch gazebo_ros gazebo.launch.py world:=worlds/empty.world

# Spawn a model from URDF
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity my_robot
```

## Simulating Sensors

### Camera Simulation
```xml
<!-- In your SDF file -->
<sensor name="camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <always_on>1</always_on>
  <update_rate>30</update_rate>
  <visualize>true</visualize>
</sensor>
```

### LiDAR Simulation
```xml
<sensor name="lidar" type="ray">
  <ray>
    <scan>
      <horizontal>
        <samples>360</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>
    </scan>
    <range>
      <min>0.1</min>
      <max>10.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
  <always_on>1</always_on>
  <update_rate>10</update_rate>
</sensor>
```

## Unity Integration

### ROS-TCP-Connector Setup
1. Install Unity Hub and Unity Editor (2022.3+)
2. Create a new 3D project
3. Install ROS-TCP-Connector via Unity Package Manager
4. Configure ROS 2 connection settings
5. Import robot models and environments

### Example: Visualizing Robot State in Unity
```csharp
using ROS2;
using UnityEngine;

public class RobotStateSubscriber : MonoBehaviour
{
    private ISubscription<geometry_msgs.msg.Pose> poseSubscriber;

    void Start()
    {
        var node = ROS2UnityCore.Instance.CreateNode("unity_robot_listener");
        poseSubscriber = node.CreateSubscription<geometry_msgs.msg.Pose>(
            "/robot/pose",
            poseMsg =>
            {
                // Update Unity GameObject transform
                transform.position = new Vector3(
                    (float)poseMsg.Position.X,
                    (float)poseMsg.Position.Y,
                    (float)poseMsg.Position.Z);

                transform.rotation = new Quaternion(
                    (float)poseMsg.Orientation.X,
                    (float)poseMsg.Orientation.Y,
                    (float)poseMsg.Orientation.Z,
                    (float)poseMsg.Orientation.W);
            });
    }
}
```

## Next Steps

Proceed to the next lesson: [Gazebo Physics Simulation](./physics-simulation)