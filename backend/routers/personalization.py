from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os

from routers.auth import get_current_user
from models import User
from config import settings

router = APIRouter(prefix="/personalization", tags=["personalization"])


class PersonalizeRequest(BaseModel):
    chapter_content: str
    chapter_title: Optional[str] = ""


class PersonalizeResponse(BaseModel):
    personalized_content: str
    expertise_level: str
    background: str
    adaptations_applied: list[str]


PERSONALIZATION_SYSTEM_PROMPT = """You are an expert educational content adapter.
You will receive technical robotics/AI textbook content and a user profile.
Adapt the content to match the user's expertise level and background.

Rules:
- beginner: Simplify jargon, add analogies, explain prerequisites, use more examples
- intermediate: Balanced depth, some jargon with brief explanations
- expert: Full technical depth, assume strong background, add advanced details

- software background: Emphasize code, algorithms, software architecture
- hardware background: Emphasize physical systems, electronics, mechanics
- both: Keep balanced mix of software and hardware

Preserve all code blocks exactly as-is. Preserve markdown formatting.
Only return the adapted content — no preamble or explanation."""


def get_openai_client():
    api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize_chapter(
    request: PersonalizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Personalize chapter content based on the authenticated user's profile.
    Adapts depth, vocabulary, and focus area to the user's expertise and background.
    """
    expertise = current_user.expertise_level   # beginner | intermediate | expert
    background = current_user.background       # software | hardware | both

    adaptations = []

    client = get_openai_client()

    if client is None:
        # No API key — return rule-based adaptation
        personalized = _rule_based_adapt(
            request.chapter_content, expertise, background, adaptations
        )
        return PersonalizeResponse(
            personalized_content=personalized,
            expertise_level=expertise,
            background=background,
            adaptations_applied=adaptations
        )

    user_profile = f"""
User Profile:
- Expertise Level: {expertise}
- Background: {background}
- Chapter: {request.chapter_title or 'Unknown'}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PERSONALIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"{user_profile}\n\nContent to adapt:\n\n{request.chapter_content}"}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        personalized = response.choices[0].message.content

        adaptations = [
            f"Adapted for {expertise} level",
            f"Focused on {background} background",
            "Vocabulary and depth adjusted",
        ]

        if expertise == "beginner":
            adaptations.append("Added simplified explanations and analogies")
        elif expertise == "expert":
            adaptations.append("Added advanced technical details")

        return PersonalizeResponse(
            personalized_content=personalized,
            expertise_level=expertise,
            background=background,
            adaptations_applied=adaptations
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Personalization failed: {str(e)}"
        )


def _rule_based_adapt(
    content: str,
    expertise: str,
    background: str,
    adaptations: list
) -> str:
    """
    Fallback rule-based adaptation when OpenAI is unavailable.
    Adds an informational header describing how the content was adapted.
    """
    header_lines = []

    if expertise == "beginner":
        header_lines.append(
            "> **Beginner Mode**: Key terms are highlighted. "
            "Focus on understanding concepts before diving into code."
        )
        adaptations.append("Added beginner guidance header")
    elif expertise == "expert":
        header_lines.append(
            "> **Expert Mode**: Full technical depth. "
            "Advanced implementation details and edge cases are included."
        )
        adaptations.append("Added expert guidance header")

    if background == "software":
        header_lines.append(
            "> **Software Focus**: Code examples and algorithms are emphasized."
        )
        adaptations.append("Added software background note")
    elif background == "hardware":
        header_lines.append(
            "> **Hardware Focus**: Physical systems and electronics are emphasized."
        )
        adaptations.append("Added hardware background note")

    if header_lines:
        header = "\n".join(header_lines) + "\n\n---\n\n"
        return header + content

    adaptations.append("No adaptation needed (intermediate/both)")
    return content


@router.get("/profile-summary")
async def get_personalization_summary(
    current_user: User = Depends(get_current_user)
):
    """Return a summary of how content will be personalized for this user."""
    expertise = current_user.expertise_level
    background = current_user.background

    descriptions = {
        "beginner": "Content will use simpler language, more analogies, and step-by-step explanations.",
        "intermediate": "Content maintains technical depth with brief explanations of advanced concepts.",
        "expert": "Content uses full technical depth, assumes strong background, includes advanced details.",
    }

    focus = {
        "software": "Code, algorithms, and software architecture will be emphasized.",
        "hardware": "Physical systems, electronics, and mechanics will be emphasized.",
        "both": "Balanced coverage of software and hardware aspects.",
    }

    return {
        "expertise_level": expertise,
        "background": background,
        "expertise_description": descriptions.get(expertise, ""),
        "background_focus": focus.get(background, ""),
        "preferred_language": current_user.preferred_language,
    }
