import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    auth_router,
    country_router,
    garment_router,
    healtcheck_router,
    look_router,
    user_router,
)
from app.core import country_service

# Use uvicorn's main logger so startup logs are visible by default
logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading country list into cache at startup...")
    country_service.get_countries_list()
    yield


app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify domains instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router mounting
app.include_router(healtcheck_router.router)
app.include_router(auth_router.router, prefix="/api/v1/auth")
app.include_router(garment_router.router, prefix="/api/v1/garments")
app.include_router(look_router.router, prefix="/api/v1/looks")
app.include_router(country_router.router, prefix="/api/v1/countries")
app.include_router(user_router.router, prefix="/api/v1/users")
