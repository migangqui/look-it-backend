from fastapi import APIRouter

# Router for healthcheck
router = APIRouter()

@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
