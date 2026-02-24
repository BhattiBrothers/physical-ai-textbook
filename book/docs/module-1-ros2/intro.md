---
sidebar_position: 1
---

# Introduction to ROS 2

Robot Operating System 2 (ROS 2) is the foundational middleware for modern robotics. In this module, you'll learn how ROS 2 enables communication between different components of a robotic system, forming the "nervous system" of your humanoid robot.

## What is ROS 2?

ROS 2 is a set of software libraries and tools for building robot applications. It provides:
- **Nodes**: Individual processes that perform computations
- **Topics**: Named buses for nodes to exchange messages
- **Services**: Request/response interactions between nodes
- **Actions**: Long-running tasks with feedback

Unlike its predecessor ROS 1, ROS 2 offers:
- Real-time capabilities
- Support for multiple DDS implementations
- Improved security features
- Cross-platform support (Linux, Windows, macOS)

## Module Learning Objectives

By the end of this module, you will be able to:
1. Install and configure ROS 2 Humble or Iron
2. Create ROS 2 packages with Python
3. Implement nodes, topics, services, and actions
4. Understand URDF (Unified Robot Description Format) for humanoids
5. Bridge Python AI agents to ROS 2 controllers using rclpy

## Weekly Breakdown

### Week 1-2: Introduction to Physical AI
- Foundations of Physical AI and embodied intelligence
- From digital AI to robots that understand physical laws
- Overview of humanoid robotics landscape
- Sensor systems: LIDAR, cameras, IMUs, force/torque sensors

### Week 3-5: ROS 2 Fundamentals
- ROS 2 architecture and core concepts
- Nodes, topics, services, and actions
- Building ROS 2 packages with Python
- Launch files and parameter management

## Prerequisites

Before starting this module, ensure you have:
- Ubuntu 22.04 LTS (recommended) or Windows with WSL2
- Basic Python programming knowledge
- Familiarity with Linux command line
- Understanding of basic robotics concepts

## Installation

```bash
# Set up ROS 2 Humble (Ubuntu 22.04)
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Install ROS 2
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-humble-desktop

# Source ROS 2 in your shell
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Next Steps

Proceed to the next lesson: [ROS 2 Nodes and Topics](./nodes-and-topics)