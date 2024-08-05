from fastapi import APIRouter
from app.utils.security import secure_data

router = APIRouter()

@router.post("/secure_data/")
async def secure_data_endpoint():
    status = secure_data()
    return {"status": status}