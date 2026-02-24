---
sidebar_position: 2
---

# ROS 2 Nodes and Topics

Nodes and topics form the core communication model in ROS 2. In this lesson, you'll learn how to create nodes that publish and subscribe to topics, enabling different parts of your robotic system to exchange information.

## What are Nodes?

A **node** is a process that performs computation. Each node is responsible for a single, modular purpose in a robotic system. For example:
- A sensor node that reads data from a camera
- A perception node that processes images to detect objects
- A control node that calculates motor commands
- A planning node that determines the robot's path

## What are Topics?

**Topics** are named buses over which nodes exchange messages. Topics implement a publish/subscribe paradigm:
- **Publishers** send messages to a topic
- **Subscribers** receive messages from a topic
- Multiple nodes can publish to the same topic
- Multiple nodes can subscribe to the same topic

## Creating Your First ROS 2 Node

Let's create a simple Python node that publishes a "Hello World" message.

### 1. Create a ROS 2 Package

```bash
# Navigate to your ROS 2 workspace
cd ~/ros2_ws/src

# Create a new package
ros2 pkg create --build-type ament_python hello_world_py

# Navigate to the package
cd hello_world_py/hello_world_py
```

### 2. Create the Publisher Node

Create a file called `publisher_node.py`:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class HelloWorldPublisher(Node):
    def __init__(self):
        super().__init__('hello_world_publisher')
        self.publisher_ = self.create_publisher(String, 'hello_topic', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.counter}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = HelloWorldPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3. Create the Subscriber Node

Create a file called `subscriber_node.py`:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class HelloWorldSubscriber(Node):
    def __init__(self):
        super().__init__('hello_world_subscriber')
        self.subscription = self.create_subscription(
            String,
            'hello_topic',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = HelloWorldSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 4. Update package.xml and setup.py

Make sure your `setup.py` includes the entry points:

```python
entry_points={
    'console_scripts': [
        'publisher_node = hello_world_py.publisher_node:main',
        'subscriber_node = hello_world_py.subscriber_node:main',
    ],
}
```

### 5. Build and Run

```bash
# Build the package
cd ~/ros2_ws
colcon build --packages-select hello_world_py

# Source the workspace
source install/setup.bash

# Run the publisher in one terminal
ros2 run hello_world_py publisher_node

# Run the subscriber in another terminal
ros2 run hello_world_py subscriber_node
```

## ROS 2 Message Types

ROS 2 provides many built-in message types in the `std_msgs` package:
- `String`: Text data
- `Int32`, `Float64`: Numerical data
- `Bool`: Boolean values
- `Header`: Timestamp and frame ID

You can also create custom message types for your specific application.

## Best Practices for Nodes and Topics

1. **Single Responsibility**: Each node should do one thing well
2. **Meaningful Names**: Use descriptive names for nodes and topics
3. **Topic Namespaces**: Organize topics hierarchically (e.g., `/sensors/camera/image_raw`)
4. **Quality of Service (QoS)**: Configure appropriate QoS profiles for your use case
5. **Error Handling**: Implement robust error handling in callbacks

## Common Patterns

### Transformations with tf2
```python
from geometry_msgs.msg import TransformStamped
import tf2_ros

# Create a transform broadcaster
self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

# Create and publish a transform
t = TransformStamped()
t.header.stamp = self.get_clock().now().to_msg()
t.header.frame_id = 'world'
t.child_frame_id = 'robot_base'
t.transform.translation.x = 1.0
t.transform.rotation.w = 1.0
self.tf_broadcaster.sendTransform(t)
```

### Parameter Server
```python
# Declare a parameter
self.declare_parameter('publish_rate', 1.0)

# Get parameter value
rate = self.get_parameter('publish_rate').get_parameter_value().double_value
```

## Next Lesson

In the next lesson, we'll explore **ROS 2 Services and Actions**, which enable request/response and long-running task patterns.