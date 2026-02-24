---
sidebar_position: 2
---

# Gazebo Physics Simulation

Physics simulation is at the heart of creating realistic digital twins. Gazebo provides multiple physics engines and comprehensive simulation capabilities for testing robotic systems in virtual environments before deploying to real hardware.

## Physics Engines in Gazebo

Gazebo supports several physics engines, each with different characteristics:

### ODE (Open Dynamics Engine) - Default
- **Strengths**: Stable, mature, good for general robotics
- **Limitations**: Less accurate for complex contacts
- **Use Case**: General robotic simulation, education

### Bullet
- **Strengths**: Excellent for games, fast collision detection
- **Limitations**: Less precise for scientific applications
- **Use Case**: Rapid prototyping, game-like simulations

### Simbody
- **Strengths**: Medical and biomechanical simulations
- **Limitations**: Slower, more complex setup
- **Use Case**: Humanoid robotics, biomechanics

### DART (Dynamic Animation and Robotics Toolkit)
- **Strengths**: Accurate, research-oriented
- **Limitations**: Computational expensive
- **Use Case**: Research, high-fidelity simulations

## Setting Up Physics Simulation

### Basic World File with Physics Configuration
```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="physics_demo">

    <!-- Physics Engine Configuration -->
    <physics name="default_physics" default="true" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
      <max_contacts>20</max_contacts>

      <ode>
        <solver>
          <type>quick</type>
          <iters>50</iters>
          <sor>1.3</sor>
        </solver>
        <constraints>
          <cfm>0.0</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
    </physics>

    <!-- Gravity Configuration -->
    <gravity>0 0 -9.81</gravity>

    <!-- Lighting -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Ground Plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Simple Box for Physics Demonstration -->
    <model name="falling_box">
      <pose>0 0 2 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.5 0.5 0.5</size>
            </box>
          </geometry>
          <surface>
            <contact>
              <ode>
                <min_depth>0.001</min_depth>
                <max_vel>100.0</max_vel>
              </ode>
            </contact>
            <friction>
              <ode>
                <mu>0.8</mu>
                <mu2>0.8</mu2>
              </ode>
              <torsional>
                <coefficient>0.5</coefficient>
              </torsional>
            </friction>
            <bounce>
              <restitution_coefficient>0.3</restitution_coefficient>
              <threshold>1000.0</threshold>
            </bounce>
          </surface>
        </collision>

        <visual name="visual">
          <geometry>
            <box>
              <size>0.5 0.5 0.5</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.2 0.2 1</ambient>
            <diffuse>0.8 0.2 0.2 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>

        <inertial>
          <mass>5.0</mass>
          <inertia>
            <ixx>0.104167</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.104167</iyy>
            <iyz>0</iyz>
            <izz>0.104167</izz>
          </inertia>
        </inertial>
      </link>
    </model>

    <!-- Second Box for Collision Demonstration -->
    <model name="static_box">
      <pose>1 0 0.25 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 0.5</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 0.5</size>
            </box>
          </geometry>
          <material>
            <ambient>0.2 0.8 0.2 1</ambient>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
```

## Launching the Physics Simulation

### ROS 2 Launch File
```python
# physics_demo.launch.py
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Path to this package
    pkg_path = get_package_share_directory('my_robot_simulation')

    # Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={
            'world': os.path.join(pkg_path, 'worlds', 'physics_demo.world'),
            'verbose': 'true',
            'physics': 'ode',
            'extra_gazebo_args': '--verbose'
        }.items()
    )

    # Spawn the falling box
    spawn_box = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'falling_box', '-file',
                   os.path.join(pkg_path, 'models', 'falling_box.sdf')],
        output='screen'
    )

    # ROS 2 node to monitor physics
    physics_monitor = Node(
        package='my_robot_simulation',
        executable='physics_monitor.py',
        name='physics_monitor',
        output='screen'
    )

    return LaunchDescription([
        gazebo_launch,
        spawn_box,
        physics_monitor
    ])
```

### Physics Monitoring Script
```python
#!/usr/bin/env python3
# physics_monitor.py
import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import LinkStates
from geometry_msgs.msg import Pose, Twist
import numpy as np

class PhysicsMonitor(Node):
    def __init__(self):
        super().__init__('physics_monitor')

        # Subscribe to link states
        self.subscription = self.create_subscription(
            LinkStates,
            '/gazebo/link_states',
            self.link_states_callback,
            10
        )

        # Track box state
        self.box_position = None
        self.box_velocity = None
        self.last_time = self.get_clock().now()

        # Physics validation
        self.gravity = 9.81  # m/s²
        self.tolerance = 0.1  # 10% tolerance

        self.get_logger().info('Physics monitor started')

    def link_states_callback(self, msg):
        # Find our falling box
        try:
            box_index = msg.name.index('falling_box::link')

            # Get current pose and twist
            current_pose = msg.pose[box_index]
            current_twist = msg.twist[box_index]

            current_time = self.get_clock().now()
            dt = (current_time - self.last_time).nanoseconds / 1e9

            if dt > 0 and self.box_position is not None:
                # Calculate expected free fall
                expected_drop = 0.5 * self.gravity * dt**2
                actual_drop = self.box_position.z - current_pose.position.z

                # Validate physics
                if abs(actual_drop - expected_drop) / expected_drop < self.tolerance:
                    self.get_logger().info(
                        f'Physics validated: Expected drop={expected_drop:.3f}m, '
                        f'Actual drop={actual_drop:.3f}m'
                    )
                else:
                    self.get_logger().warn(
                        f'Physics deviation: Expected drop={expected_drop:.3f}m, '
                        f'Actual drop={actual_drop:.3f}m'
                    )

            # Update state
            self.box_position = current_pose.position
            self.box_velocity = current_twist
            self.last_time = current_time

        except ValueError:
            # Box not found yet
            pass

def main(args=None):
    rclpy.init(args=args)
    node = PhysicsMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Advanced Physics: Joints and Constraints

### Revolute Joint Example
```xml
<!-- In your SDF model -->
<model name="pendulum">
  <pose>0 0 3 0 0 0</pose>

  <link name="base">
    <pose>0 0 0 0 0 0</pose>
    <collision name="collision">
      <geometry>
        <cylinder>
          <radius>0.05</radius>
          <length>0.1</length>
        </cylinder>
      </geometry>
    </collision>
    <visual name="visual">
      <geometry>
        <cylinder>
          <radius>0.05</radius>
          <length>0.1</length>
        </cylinder>
      </geometry>
      <material>
        <ambient>0.5 0.5 0.5 1</ambient>
      </material>
    </visual>
    <inertial>
      <mass>0.1</mass>
      <inertia>
        <ixx>0.0001</ixx>
        <iyy>0.0001</iyy>
        <izz>0.0001</izz>
      </inertia>
    </inertial>
  </link>

  <link name="arm">
    <pose>0 0 -1 0 0 0</pose>
    <collision name="collision">
      <geometry>
        <cylinder>
          <radius>0.02</radius>
          <length>2</length>
        </cylinder>
      </geometry>
    </collision>
    <visual name="visual">
      <geometry>
        <cylinder>
          <radius>0.02</radius>
          <length>2</length>
        </cylinder>
      </geometry>
      <material>
        <ambient>0.8 0.2 0.2 1</ambient>
      </material>
    </visual>
    <inertial>
      <mass>1.0</mass>
      <inertia>
        <ixx>0.333</ixx>
        <iyy>0.333</iyy>
        <izz>0.001</izz>
      </inertia>
    </inertial>
  </link>

  <joint name="base_to_arm" type="revolute">
    <parent>base</parent>
    <child>arm</child>
    <axis>
      <xyz>0 1 0</xyz>
      <limit>
        <lower>-3.14159</lower>
        <upper>3.14159</upper>
        <effort>100</effort>
        <velocity>10</velocity>
      </limit>
      <dynamics>
        <damping>0.1</damping>
        <friction>0.01</friction>
      </dynamics>
    </axis>
    <physics>
      <ode>
        <cfm_damping>1</cfm_damping>
      </ode>
    </physics>
  </joint>
</model>
```

### Python Controller for Pendulum
```python
#!/usr/bin/env python3
# pendulum_controller.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import numpy as np

class PendulumController(Node):
    def __init__(self):
        super().__init__('pendulum_controller')

        # Publisher for joint effort
        self.effort_pub = self.create_publisher(
            Float64,
            '/pendulum/base_to_arm/effort',
            10
        )

        # Control parameters
        self.kp = 50.0  # Proportional gain
        self.kd = 5.0   # Derivative gain
        self.target_angle = 0.0  # Upright position

        # Create control timer
        self.timer = self.create_timer(0.01, self.control_callback)

        self.get_logger().info('Pendulum controller started')

    def control_callback(self):
        # In a real implementation, you would:
        # 1. Read current joint state from /joint_states
        # 2. Calculate error = target - current
        # 3. Apply PD control: effort = kp*error + kd*derror/dt

        # For this example, we'll apply a sinusoidal effort
        current_time = self.get_clock().now().nanoseconds / 1e9
        effort = 10.0 * np.sin(2.0 * np.pi * 0.5 * current_time)

        # Publish effort command
        msg = Float64()
        msg.data = effort
        self.effort_pub.publish(msg)

        self.get_logger().debug(f'Applied effort: {effort:.2f} Nm')

def main(args=None):
    rclpy.init(args=args)
    node = PendulumController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Physics Debugging and Visualization

### Visualizing Contact Forces
```python
#!/usr/bin/env python3
# contact_visualizer.py
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point, Vector3
from std_msgs.msg import ColorRGBA
from gazebo_msgs.msg import ContactsState

class ContactVisualizer(Node):
    def __init__(self):
        super().__init__('contact_visualizer')

        # Subscribe to contact states
        self.subscription = self.create_subscription(
            ContactsState,
            '/gazebo/contacts',
            self.contacts_callback,
            10
        )

        # Publisher for visualization markers
        self.marker_pub = self.create_publisher(
            MarkerArray,
            '/visualization/contacts',
            10
        )

        self.get_logger().info('Contact visualizer started')

    def contacts_callback(self, msg):
        marker_array = MarkerArray()

        for contact_state in msg.states:
            for contact in contact_state.contact_positions:
                # Create arrow marker for contact force
                marker = Marker()
                marker.header.frame_id = 'world'
                marker.header.stamp = self.get_clock().now().to_msg()
                marker.ns = 'contact_forces'
                marker.id = hash(contact_state.collision1_name + contact_state.collision2_name) % 1000
                marker.type = Marker.ARROW
                marker.action = Marker.ADD

                # Set pose (force direction)
                marker.pose.position.x = contact.x
                marker.pose.position.y = contact.y
                marker.pose.position.z = contact.z

                # Scale based on force magnitude
                force_magnitude = 0.1  # Simplified - would use actual force data
                marker.scale = Vector3(x=0.02, y=0.04, z=force_magnitude)

                # Color based on force magnitude
                marker.color = ColorRGBA(r=1.0, g=0.0, b=0.0, a=0.8)

                marker_array.markers.append(marker)

        # Publish markers
        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    node = ContactVisualizer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Best Practices for Physics Simulation

### 1. Start Simple
- Begin with simple shapes and single joints
- Gradually increase complexity
- Validate each component independently

### 2. Parameter Tuning
- Adjust physics parameters incrementally
- Document all parameter changes
- Create parameter sweeps for optimization

### 3. Validation
- Compare simulation results with analytical solutions
- Use unit tests for physics components
- Implement sanity checks in monitoring scripts

### 4. Performance
- Use appropriate level of detail (LOD)
- Disable visualization for batch simulations
- Consider simplified collision geometries

### 5. Reproducibility
- Seed random number generators
- Record all simulation parameters
- Version control world and model files

## Next Steps

After mastering Gazebo physics simulation, proceed to:
1. **Sensor Simulation**: Add cameras, LiDAR, and IMUs to your models
2. **ROS 2 Integration**: Connect Gazebo simulations to ROS 2 control systems
3. **Unity Visualization**: Create high-fidelity visualizations of your physics simulations
4. **NVIDIA Isaac**: Move to photorealistic simulation with ray tracing

Remember: A good physics simulation is not about perfect accuracy, but about capturing the essential dynamics needed for your specific application.