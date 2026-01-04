from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_tryon():
    return {"message": "Tryon endpoint"}
