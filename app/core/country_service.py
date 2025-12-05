import json
from typing import List, Optional

from app.core import gemini_service


_countries_cache: Optional[List[str]] = None


def get_countries_list() -> List[str]:
    global _countries_cache

    if _countries_cache is not None:
        return _countries_cache

    prompt = (
        "Dame una lista de los country code (ej: ES, GB, US) "
        "de todos los países en formato lista JSON. "
        "Solo la lista sin texto adicional ni ```json``` ni texto envolvente."
    )
    response = gemini_service.generate_from_prompt(prompt)
    countries = json.loads(response or "[]")

    _countries_cache = countries
    return countries
