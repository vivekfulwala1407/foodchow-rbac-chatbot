from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from pydantic import SecretStr

from app.config import get_settings

settings = get_settings()


def generate_follow_up_questions(
    query: str,
    answer: str,
    role: str,
    sources: list[str],
) -> list[str]:
    """
    Generates 3 intelligent follow-up questions based on:
    - What the user just asked
    - What the AI just answered
    - The user's role (so suggestions stay within their access)
    """
    try:
        llm = ChatGroq(
            api_key=SecretStr(settings.groq_api_key),
            model=settings.llm_model,
            temperature=0.7,
            max_tokens=200,
        )

        prompt = f"""You are an AI assistant helping a {role} team member at a FinTech company.

They just asked: "{query}"

The answer they received was:
"{answer[:500]}"

The answer came from these documents: {", ".join(sources) if sources else "general knowledge"}

Generate exactly 3 short, relevant follow-up questions they might want to ask next.
These questions must:
1. Be directly related to the topic just discussed
2. Be appropriate for someone with {role} role access
3. Be concise (under 12 words each)
4. Be genuinely useful and different from each other

Return ONLY the 3 questions, one per line, no numbering, no bullets, no extra text.
Example format:
What was the breakdown by department?
How does this compare to last quarter?
What are the projections for next quarter?"""

        response = llm.invoke([HumanMessage(content=prompt)])

        # Explicitly cast to str — fixes Pylance warning
        raw_content: str = str(response.content).strip()

        # Parse — split by newline, clean up, take first 3
        questions = [
            q.strip().lstrip("123.-) ")
            for q in raw_content.split("\n")
            if q.strip()
        ][:3]

        # Validate
        valid = [
            q for q in questions
            if len(q) > 5 and len(q) < 120
        ]

        return valid[:3]

    except Exception:
        return []