from fastapi import APIRouter

from app.core.country_service import get_countries_list


router = APIRouter()


@router.get("")
async def list_countries():
    """
    Return a list of country codes (e.g. ES, US, GB).
    """
    return get_countries_list()

