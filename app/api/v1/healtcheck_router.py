from fastapi import APIRouter

# Router para healthcheck
router = APIRouter()

@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
