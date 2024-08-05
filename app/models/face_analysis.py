from sqlalchemy import Column, Integer, String
from . import Base

class FaceAnalysis(Base):
    __tablename__ = "face_analysis"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String, index=True)
    emotion = Column(String)
    age = Column(Integer)
    gender = Column(String)
    race = Column(String)