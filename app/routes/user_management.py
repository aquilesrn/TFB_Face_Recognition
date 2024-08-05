from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.config import Config
from app.models import SessionLocal

class UserCreate(BaseModel):
    username: str
    password: str

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create_user/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserService.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    created_user = UserService.create_user(db, username=user.username, password=user.password)
    return {"status": f"User {created_user.username} created successfully"}
