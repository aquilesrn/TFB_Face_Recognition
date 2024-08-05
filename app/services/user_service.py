from sqlalchemy.orm import Session
from app.models.user import User
from app.config import Config
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_user(db: Session, username: str, password: str):
        hashed_password = UserService.get_password_hash(password)
        db_user = User(username=username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
