import json
from datetime import date
from typing import Optional
from urllib import parse, request

from fastapi import HTTPException
from app.settings import OPENWEATHERMAP_API_KEY


OPENWEATHER_WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"


def _fetch_json(url: str):
    try:
        with request.urlopen(url, timeout=10) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"OpenWeatherMap error: HTTP {response.status}",
                )
            data = response.read()
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - network failure path
        raise HTTPException(
            status_code=502,
            detail=f"Error calling OpenWeatherMap: {exc}",
        ) from exc

    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="Invalid response from OpenWeatherMap",
        ) from exc


async def _geocode_city_country(
    city: str,
    country_code: str,
) -> tuple[float, float]:
    params = parse.urlencode(
        {
            "q": f"{city},{country_code}",
            "limit": 1,
            "appid": OPENWEATHERMAP_API_KEY,
        }
    )
    url = f"{OPENWEATHER_GEOCODING_URL}?{params}"

    payload = _fetch_json(url)

    if not isinstance(payload, list) or not payload:
        raise HTTPException(
            status_code=404,
            detail="Location not found for given city and country",
        )

    first = payload[0]
    try:
        lat = float(first["lat"])
        lon = float(first["lon"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unexpected geocoding response from OpenWeatherMap",
        ) from exc

    return lat, lon


async def get_temperature_c_for_city(
    city: str,
    country_code: str,
    target_date: Optional[date] = None,
) -> float:
    latitude, longitude = await _geocode_city_country(city=city, country_code=country_code)

    params = parse.urlencode(
        {
            "lat": latitude,
            "lon": longitude,
            "appid": OPENWEATHERMAP_API_KEY,
            "units": "metric",
        }
    )
    url = f"{OPENWEATHER_WEATHER_BASE_URL}/weather?{params}"

    payload = _fetch_json(url)

    try:
        temp_c = float(payload["main"]["temp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unexpected response structure from OpenWeatherMap",
        ) from exc

    return temp_c
