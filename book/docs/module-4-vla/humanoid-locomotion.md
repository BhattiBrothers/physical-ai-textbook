---
sidebar_position: 2
---

# Humanoid Robot Kinematics & Locomotion

Humanoid robots are among the most mechanically complex systems in robotics. This lesson covers the fundamentals of bipedal kinematics, dynamic balance, and locomotion control needed to build walking robots.

## Humanoid Robot Anatomy

A typical humanoid robot has 30–50 degrees of freedom (DoF):

| Body Part | DoF | Joint Types |
|-----------|-----|-------------|
| Each leg | 6 | Hip (3), Knee (1), Ankle (2) |
| Each arm | 7 | Shoulder (3), Elbow (1), Wrist (3) |
| Torso | 2 | Waist pitch, roll |
| Head | 3 | Pan, tilt, roll |
| Each hand | 5–15 | Fingers |

## Forward & Inverse Kinematics

### Forward Kinematics with URDF

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np

# Using ikpy for kinematic calculations
# pip install ikpy
from ikpy.chain import Chain
from ikpy.utils import geometry

class HumanoidKinematics:
    def __init__(self, urdf_path: str):
        # Load kinematic chains from URDF
        self.left_leg = Chain.from_urdf_file(
            urdf_path,
            base_elements=["pelvis"],
            last_link_vector=[0, 0, -0.1],
            active_links_mask=[False, True, True, True, True, True, True, False]
        )
        self.right_leg = Chain.from_urdf_file(
            urdf_path,
            base_elements=["pelvis"],
            last_link_vector=[0, 0, -0.1],
        )

    def compute_fk(self, joint_angles: np.ndarray) -> np.ndarray:
        """Compute end-effector position from joint angles."""
        transform = self.left_leg.forward_kinematics(joint_angles)
        return transform[:3, 3]  # Extract position

    def compute_ik(self, target_position: np.ndarray,
                   initial_angles: np.ndarray = None) -> np.ndarray:
        """
        Compute joint angles to reach target foot position.
        Uses iterative numerical IK solver.
        """
        if initial_angles is None:
            initial_angles = np.zeros(len(self.left_leg.links))

        result = self.left_leg.inverse_kinematics(
            target_position=target_position,
            initial_position=initial_angles,
            max_iter=100,
            tolerance=1e-4
        )
        return result

# Example usage
kin = HumanoidKinematics("robot.urdf")
foot_pos = np.array([0.0, -0.15, -0.8])  # 80 cm below pelvis, offset laterally
joint_angles = kin.compute_ik(foot_pos)
print(f"Required joint angles: {np.degrees(joint_angles)}")
```

### Jacobian-Based Control

```python
import numpy as np
from scipy.linalg import pinv

def jacobian_ik(jacobian_fn, target_vel, joint_angles, dt=0.01):
    """
    Velocity-based IK using Jacobian pseudo-inverse.
    Useful for smooth real-time control.
    """
    J = jacobian_fn(joint_angles)          # 6×n Jacobian matrix
    J_pinv = pinv(J)                       # Moore-Penrose pseudo-inverse

    joint_velocities = J_pinv @ target_vel # n-dimensional joint velocity
    new_angles = joint_angles + joint_velocities * dt

    return new_angles, joint_velocities
```

## Zero-Moment Point (ZMP) Theory

ZMP is the foundation of bipedal balance. A robot is stable if the ZMP lies within the support polygon (the convex hull of foot contact points).

```
           ┌──────────────────────────┐
           │     Support Polygon      │
           │  ┌────────────────────┐  │
           │  │   Stable ZMP Zone  │  │
           │  │         ×          │  │
           │  │       (ZMP)        │  │
           │  └────────────────────┘  │
           │  Left Foot   Right Foot  │
           └──────────────────────────┘

   If ZMP exits polygon → robot falls!
```

```python
import numpy as np

def compute_zmp(
    com_position: np.ndarray,    # Center of Mass [x, y, z]
    com_acceleration: np.ndarray, # CoM acceleration [ax, ay, az]
    total_mass: float,
    g: float = 9.81
) -> np.ndarray:
    """
    Compute Zero-Moment Point from CoM dynamics.
    ZMP = CoM_xy - (CoM_z / (g + az)) * [ax, ay]
    """
    ax, ay, az = com_acceleration
    z_com = com_position[2]

    zmp_x = com_position[0] - (z_com / (g + az)) * ax
    zmp_y = com_position[1] - (z_com / (g + az)) * ay

    return np.array([zmp_x, zmp_y])

def is_stable(zmp: np.ndarray, support_polygon: np.ndarray) -> bool:
    """Check if ZMP lies within convex support polygon."""
    from scipy.spatial import ConvexHull
    hull = ConvexHull(support_polygon)

    # Point-in-convex-hull test
    for eq in hull.equations:
        if eq[:2] @ zmp + eq[2] > 1e-6:
            return False
    return True

# Example
com_pos = np.array([0.0, 0.0, 0.9])   # 90 cm tall CoM
com_acc = np.array([0.1, 0.0, 0.0])   # Slight forward acceleration
zmp = compute_zmp(com_pos, com_acc, total_mass=60.0)
print(f"ZMP: ({zmp[0]:.4f}, {zmp[1]:.4f})")
```

## Gait Planning

### Central Pattern Generator (CPG)

CPGs are biologically inspired oscillators that generate rhythmic locomotion patterns without requiring complex planning.

```python
import numpy as np
import matplotlib.pyplot as plt

class CPGOscillator:
    """
    Matsuoka neuron oscillator for rhythmic gait generation.
    Produces natural, adaptive walking patterns.
    """
    def __init__(self, frequency: float = 1.0, amplitude: float = 1.0):
        self.omega = 2 * np.pi * frequency  # Angular frequency
        self.amplitude = amplitude
        self.phase = 0.0
        self.dt = 0.01  # 100 Hz control loop

    def step(self) -> tuple:
        """
        Returns (left_leg_signal, right_leg_signal) — 180° out of phase.
        """
        self.phase += self.omega * self.dt
        left  = self.amplitude * np.sin(self.phase)
        right = self.amplitude * np.sin(self.phase + np.pi)  # Opposite phase
        return left, right

class BipedalGaitPlanner:
    """
    Full gait planner combining CPG with foot placement.
    """
    def __init__(self, step_length: float = 0.3, step_height: float = 0.1):
        self.step_length = step_length
        self.step_height = step_height
        self.cpg = CPGOscillator(frequency=1.0)
        self.step_count = 0

    def get_foot_trajectory(self, t: float, is_left: bool) -> np.ndarray:
        """
        Bezier curve foot trajectory for swing phase.
        Returns [x, y, z] foot position.
        """
        phase = (t % 1.0)  # Normalized gait cycle [0, 1]

        # Swing phase: 0.0 to 0.5
        # Stance phase: 0.5 to 1.0
        if is_left:
            phase = phase
        else:
            phase = (phase + 0.5) % 1.0  # Offset by half cycle

        if phase < 0.5:  # Swing
            s = phase / 0.5  # Normalized swing phase [0, 1]
            x = self.step_length * s
            z = self.step_height * np.sin(np.pi * s)  # Parabolic arc
        else:  # Stance
            s = (phase - 0.5) / 0.5
            x = self.step_length * (1.0 - s)
            z = 0.0

        return np.array([x, 0.0, z])

    def update(self) -> dict:
        """Get joint commands for current timestep."""
        left_signal, right_signal = self.cpg.step()

        return {
            "left_hip_pitch":   left_signal * 0.3,
            "left_knee_pitch":  abs(left_signal) * 0.5,
            "left_ankle_pitch": -left_signal * 0.2,
            "right_hip_pitch":  right_signal * 0.3,
            "right_knee_pitch": abs(right_signal) * 0.5,
            "right_ankle_pitch":-right_signal * 0.2,
        }
```

### Whole-Body Control (WBC)

Whole-Body Control distributes tasks across all joints while respecting physical constraints.

```python
import numpy as np
from scipy.linalg import pinv

class WholeBodyController:
    """
    Hierarchical whole-body controller for humanoid.
    Tasks are prioritized: balance > motion > posture.
    """

    def __init__(self, n_joints: int = 30):
        self.n_joints = n_joints
        self.tasks = []  # Ordered list of (priority, task_name, Jacobian, desired_vel)

    def add_task(self, priority: int, name: str, jacobian: np.ndarray,
                 desired_vel: np.ndarray):
        self.tasks.append({
            "priority": priority,
            "name": name,
            "J": jacobian,
            "xd": desired_vel
        })
        self.tasks.sort(key=lambda t: t["priority"])

    def compute_joint_commands(self) -> np.ndarray:
        """
        Compute joint velocities satisfying all tasks in priority order.
        Uses null-space projection to avoid task conflicts.
        """
        q_dot = np.zeros(self.n_joints)
        N = np.eye(self.n_joints)  # Null-space projector

        for task in self.tasks:
            J = task["J"]
            xd = task["xd"]

            # Projected task Jacobian
            JN = J @ N
            JN_pinv = pinv(JN)

            # Task contribution (only in null space of higher-priority tasks)
            q_dot += JN_pinv @ (xd - J @ q_dot)

            # Update null-space projector
            N = N - JN_pinv @ JN

        return q_dot
```

## ROS 2 Integration

### Publishing Joint Commands

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import time

class LocomotionController(Node):
    def __init__(self):
        super().__init__('locomotion_controller')

        self.joint_pub = self.create_publisher(
            JointState, '/joint_commands', 10
        )

        self.gait = BipedalGaitPlanner(step_length=0.25, step_height=0.08)
        self.timer = self.create_timer(0.01, self.control_loop)  # 100 Hz
        self.t = 0.0

        self.get_logger().info('Locomotion controller started')

    def control_loop(self):
        commands = self.gait.update()

        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(commands.keys())
        msg.position = list(commands.values())

        self.joint_pub.publish(msg)
        self.t += 0.01

def main():
    rclpy.init()
    controller = LocomotionController()
    rclpy.spin(controller)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Key Humanoid Platforms

| Platform | Manufacturer | DoF | Notable Feature |
|----------|-------------|-----|-----------------|
| Atlas | Boston Dynamics | 28 | Hydraulic actuators, extreme agility |
| Digit | Agility Robotics | 30 | Designed for logistics |
| Optimus | Tesla | 28 | Electric, mass-producible |
| H1 | Unitree | 19 | Affordable research platform |
| GR-1 | Fourier Intelligence | 40 | ROS 2 native |

## Exercises

1. Implement a ZMP-based stability checker for a static standing pose
2. Tune CPG parameters (frequency, amplitude) to achieve stable walking in Gazebo
3. Add a swing-leg trajectory to your CPG gait planner and visualize in matplotlib
4. Implement a 2-task WBC: (1) balance the CoM, (2) wave the right arm

## Next Steps

Proceed to the next lesson: [Voice Interface Implementation](./voice-interface)
