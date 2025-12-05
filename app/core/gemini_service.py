from app.config.google_config import genai_client


_DEFAULT_MODEL = "gemini-flash-latest"

def generate_from_prompt(prompt: str) -> str:

    response = genai_client.models.generate_content(
        model=_DEFAULT_MODEL,
        contents=prompt,
    )
    return response.text or "[]"
