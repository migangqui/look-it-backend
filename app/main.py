
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth_router, garment_router, look_router, healtcheck_router, user_router


app = FastAPI()

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
app.include_router(user_router.router, prefix="/api/v1/users")
