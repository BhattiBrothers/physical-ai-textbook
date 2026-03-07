---
sidebar_position: 2
---

# Isaac Sim: Photorealistic Simulation & Synthetic Data

NVIDIA Isaac Sim provides RTX-powered photorealistic simulation that bridges the gap between virtual training and real-world deployment. This lesson covers advanced Isaac Sim workflows for generating synthetic training data and reinforcement learning.

## Photorealistic Rendering with RTX

Isaac Sim uses NVIDIA RTX ray tracing to generate physically accurate images nearly indistinguishable from real camera feeds.

### Key Rendering Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| Ray Tracing | Physically correct light simulation | Realistic shadows, reflections |
| Path Tracing | Full global illumination | Photorealistic training data |
| Domain Randomization | Random scene parameters | Sim-to-real robustness |
| Sensor Simulation | RGB, Depth, LiDAR, IMU | Multi-modal perception |

### Setting Up a Photorealistic Scene

```python
from omni.isaac.kit import SimulationApp

simulation_app = SimulationApp({
    "headless": False,
    "renderer": "RayTracedLighting",
    "width": 1280,
    "height": 720,
})

from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage

world = World(stage_units_in_meters=1.0)

# Load a photorealistic interior scene
add_reference_to_stage(
    usd_path="omniverse://localhost/NVIDIA/Assets/Scenes/Templates/Interior/SimpleRoom.usd",
    prim_path="/World/Room"
)

world.reset()
```

### Configuring Sensors

```python
from omni.isaac.sensor import Camera, LidarRtx, IMUSensor

# RGB-D Camera
camera = Camera(
    prim_path="/World/Robot/head/camera",
    position=[0.0, 0.0, 0.5],
    frequency=30,
    resolution=(640, 480),
)

# LiDAR
lidar = LidarRtx(
    prim_path="/World/Robot/base/lidar",
    position=[0.0, 0.0, 0.3],
)

# IMU
imu = IMUSensor(
    prim_path="/World/Robot/base/imu",
    name="imu",
    frequency=200,
)

camera.initialize()
lidar.initialize()
imu.initialize()
```

## Synthetic Data Generation Pipeline

```python
import numpy as np
import json, os
from PIL import Image

class SyntheticDataPipeline:
    def __init__(self, output_dir: str, num_samples: int = 1000):
        self.output_dir = output_dir
        self.num_samples = num_samples
        for d in ["rgb", "depth", "segmentation", "labels"]:
            os.makedirs(f"{output_dir}/{d}", exist_ok=True)

    def randomize_scene(self, world):
        """Domain randomization: lighting, textures, camera jitter."""
        # Randomize light intensity
        light_prim = world.stage.GetPrimAtPath("/World/DomeLight")
        if light_prim.IsValid():
            light_prim.GetAttribute("inputs:intensity").Set(
                float(np.random.uniform(500, 2000))
            )

    def capture_frame(self, frame_id: int, camera, annotations: dict):
        """Capture RGB, depth, segmentation and save."""
        rgb = camera.get_rgba()[:, :, :3]
        depth = camera.get_depth()

        Image.fromarray(rgb).save(f"{self.output_dir}/rgb/{frame_id:06d}.png")
        np.save(f"{self.output_dir}/depth/{frame_id:06d}.npy", depth)

        with open(f"{self.output_dir}/labels/{frame_id:06d}.json", "w") as f:
            json.dump(annotations, f)

    def run(self, world, camera):
        print(f"Generating {self.num_samples} samples...")
        for i in range(self.num_samples):
            self.randomize_scene(world)
            for _ in range(10):
                world.step(render=True)
            self.capture_frame(i, camera, {"image_id": i})
            if i % 100 == 0:
                print(f"  {i}/{self.num_samples} done")
        print(f"Dataset saved to {self.output_dir}")
```

## Reinforcement Learning with Isaac Gym

### Parallel Humanoid Balance Task

```python
import torch
import torch.nn as nn
from torch.distributions import Normal

class PolicyNetwork(nn.Module):
    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.actor = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim), nn.ELU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ELU(),
            nn.Linear(hidden_dim, action_dim),
        )
        self.critic = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim), nn.ELU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ELU(),
            nn.Linear(hidden_dim, 1),
        )
        self.log_std = nn.Parameter(torch.zeros(action_dim))

    def forward(self, obs):
        mean = self.actor(obs)
        dist = Normal(mean, self.log_std.exp())
        value = self.critic(obs)
        return dist, value
```

### Reward Design for Balance

```python
def compute_reward(base_height, forward_vel, joint_torques):
    """
    Reward components:
    - Stay upright (height > 0.8 m)
    - Move forward
    - Minimize energy (joint torques)
    """
    upright = torch.clamp(base_height - 0.5, 0, 1) * 2.0
    velocity = torch.clamp(forward_vel, -0.5, 1.5)
    energy_penalty = -0.001 * (joint_torques ** 2).sum(dim=-1)
    fall_penalty = (base_height < 0.3).float() * -10.0

    return upright + velocity + energy_penalty + fall_penalty
```

## Sim-to-Real Transfer

### Domain Randomization Best Practices

```python
RANDOMIZATION_RANGES = {
    "ground_friction":   (0.5, 1.5),
    "joint_damping":     (0.8, 1.2),   # multiplier
    "mass_scale":        (0.9, 1.1),
    "light_intensity":   (500, 2000),
    "action_noise_std":  (0.0, 0.05),
    "action_delay_steps":(0, 3),
}

def sample_randomization():
    return {k: np.random.uniform(lo, hi)
            for k, (lo, hi) in RANDOMIZATION_RANGES.items()}
```

### Progressive Transfer Strategy

```python
# Phase 1: Train in simulation (many episodes, no cost)
sim_policy = train_in_sim(episodes=50_000)

# Phase 2: Fine-tune on limited real data
real_data = collect_real_robot_data(episodes=500)
adapted_policy = fine_tune(sim_policy, real_data, lr=1e-4)

# Phase 3: Online adaptation during deployment
deployed = OnlineAdaptationWrapper(adapted_policy, adaptation_rate=0.001)
```

## Exercises

1. Generate a 100-sample synthetic dataset of a robot grasping objects with three different lighting conditions
2. Implement a simple pole-balancing RL task and train for 10,000 steps
3. Measure the performance drop when transferring a policy trained without domain randomization vs. with it

## Next Steps

Proceed to the next lesson: [Isaac ROS & VSLAM](./isaac-ros-vslam)
