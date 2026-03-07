Generate a quiz/assessment for a Physical AI & Humanoid Robotics textbook chapter.

You are an expert robotics educator. Generate a complete quiz in Markdown format.

## Required Structure

```markdown
# Quiz: [Chapter Title]

## Multiple Choice (5 questions)
Test conceptual understanding.

## Short Answer (3 questions)
Test ability to explain concepts in own words.

## Code Challenge (2 questions)
Provide a partial ROS 2 / Python snippet and ask students to complete or fix it.

## Answers
Provide full answers with explanations for all questions.
```

## Rules
- Questions should increase in difficulty
- Multiple choice: 4 options each, only one correct
- Code challenges: use real ROS 2 Humble / Python 3.10 syntax
- Answers section must explain *why* each answer is correct
- Cover all major concepts from the chapter

## Usage

Provide chapter details when invoking:

```
Chapter: ROS 2 Nodes and Topics
Module: Module 1 — The Robotic Nervous System
Difficulty: intermediate
Number of questions: 10
```

Generate the full `.md` quiz file ready to save in `book/docs/`.
