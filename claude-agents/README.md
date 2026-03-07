# Claude Code Subagents

This directory contains reusable Claude Code subagent skill definitions for the Physical AI & Humanoid Robotics Textbook project.

## Available Agents

| Agent | File | Purpose |
|-------|------|---------|
| Content Generator | `content-generator.md` | Generate textbook lesson content |
| Code Example Generator | `code-example-generator.md` | Generate runnable code examples |
| Quiz Generator | `quiz-generator.md` | Generate assessments and quizzes |

## How to Use

These agents are invoked via Claude Code using the `/skill` mechanism:

```bash
# In Claude Code terminal
/content-generator --topic "ROS 2 Services" --module 1

/code-example-generator --concept "VSLAM pipeline" --ros2

/quiz-generator --chapter "Isaac Sim Basics" --questions 10
```

## Agent Design Principles

1. **Reusable** — Each agent works for any lesson/topic in the course
2. **Parameterized** — Configurable via command-line arguments
3. **Consistent output** — Always produces formatted Markdown ready for the book
4. **Educationally sound** — Follows pedagogical best practices

## Adding New Agents

Create a new `.md` file in this directory with:
- **Description** — What the agent does
- **Usage** — Example invocation
- **Agent Prompt** — The system prompt / instructions
- **Output Format** — Expected output structure
- **Parameters** — Available configuration options
