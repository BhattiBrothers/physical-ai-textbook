# Physical AI & Humanoid Robotics Textbook Hackathon

## 🎯 Project Overview
An AI-native technical textbook for teaching "Physical AI & Humanoid Robotics" with integrated RAG chatbot, authentication, personalization, and Urdu translation features.

## 📋 Hackathon Requirements
This project fulfills the requirements for **Hackathon I: Create a Textbook for Teaching Physical AI & Humanoid Robotics Course**

### Base Features (100 points)
1. **AI/Spec-Driven Book Creation**: Docusaurus textbook deployed to GitHub Pages using Spec-Kit Plus and Claude Code
2. **Integrated RAG Chatbot**: Retrieval-Augmented Generation chatbot embedded in the book using OpenAI, FastAPI, Neon Postgres, and Qdrant

### Bonus Features (Up to 200 points)
3. **Claude Code Subagents**: Reusable intelligence via Claude Code Subagents and Agent Skills (50 points)
4. **Authentication & Profiling**: Signup/Signin with Better Auth including user background questionnaire (50 points)
5. **Content Personalization**: Chapter-level personalization based on user background (50 points)
6. **Urdu Translation**: Translate chapter content to Urdu (50 points)

## 🏗️ Project Structure
```
.
├── PROJECT_PLAN.md          # Complete project roadmap with all phases
├── PROGRESS.md             # Daily progress tracking
├── book/                   # Docusaurus textbook
├── backend/                # FastAPI RAG chatbot
├── frontend-chat/          # Chatbot React widget
├── claude-agents/          # Claude Code subagents
└── deployment/             # Deployment scripts
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python 3.10+
- Git
- GitHub account
- Accounts for: OpenAI, Qdrant Cloud, Neon.tech, Better Auth

### Installation
*Detailed installation instructions will be added as development progresses.*

## 📚 Course Content
The textbook covers the complete "Physical AI & Humanoid Robotics" course:

### Modules:
1. **The Robotic Nervous System (ROS 2)** - ROS 2 Nodes, Topics, Services, URDF
2. **The Digital Twin (Gazebo & Unity)** - Physics simulation, sensor simulation
3. **The AI-Robot Brain (NVIDIA Isaac)** - Isaac Sim, Isaac ROS, VSLAM, Nav2
4. **Vision-Language-Action (VLA)** - Whisper, LLM planning, Capstone project

### Weekly Breakdown (13 weeks):
- Weeks 1-2: Introduction to Physical AI
- Weeks 3-5: ROS 2 Fundamentals
- Weeks 6-7: Gazebo Simulation
- Weeks 8-10: NVIDIA Isaac Platform
- Weeks 11-12: Humanoid Robot Development
- Week 13: Conversational Robotics

## 🛠️ Technology Stack

### Frontend (Book)
- **Docusaurus** (React-based static site generator)
- **Markdown** for content
- **React** components for interactive elements

### Backend (Chatbot)
- **FastAPI** (Python web framework)
- **OpenAI API** (GPT models for RAG)
- **Qdrant Cloud** (Vector database for embeddings)
- **Neon Postgres** (Serverless PostgreSQL for user data)
- **Better Auth** (Authentication service)

### Development Tools
- **Claude Code** (AI-assisted development)
- **Spec-Kit Plus** (AI-driven book generation framework)
- **Git/GitHub** (Version control and collaboration)

## 📊 Development Plan
See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed 20-day development plan with all phases.

## 🎯 Progress Tracking
Current progress is tracked in [PROGRESS.md](PROGRESS.md).

## 🤝 Contributing
This is a hackathon submission. For contribution guidelines, please contact the project maintainer.

## 📄 License
*To be determined*

## 📞 Contact
*Contact information will be added before submission*

---

**Note:** This project is being developed for Hackathon I submission. Follow the project plan for systematic development and completion.