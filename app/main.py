from fastapi import FastAPI
from app.api.v1 import auth_router, garment_router, look_router, test_router, healtcheck_router

app = FastAPI()

# Montaje de routers
#app.include_router(auth_router.router, prefix="/api/v1/auth")
#app.include_router(garment_router.router, prefix="/api/v1/garment")
#app.include_router(look_router.router, prefix="/api/v1/look")
app.include_router(test_router.router, prefix="/api/v1/test")
app.include_router(healtcheck_router.router, prefix="")
