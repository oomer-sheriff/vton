from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_search():
    return {"message": "Search endpoint"}
