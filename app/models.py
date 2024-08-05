from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    images = relationship('Image', back_populates='user')

class Model(Base):
    __tablename__ = 'models'
    model_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)

class Image(Base):
    __tablename__ = 'images'
    image_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    user = relationship('User', back_populates='images')
    analyses = relationship('Analysis', back_populates='image')

class Analysis(Base):
    __tablename__ = 'analyses'
    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey('images.image_id'), nullable=False)
    model_id = Column(Integer, ForeignKey('models.model_id'), nullable=False)
    analysis_time = Column(DateTime, default=datetime.utcnow)
    result_data = Column(JSON)
    image = relationship('Image', back_populates='analyses')
    model = relationship('Model')
    metrics = relationship('Metric', back_populates='analysis')

class Metric(Base):
    __tablename__ = 'metrics'
    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('analyses.analysis_id'), nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    analysis = relationship('Analysis', back_populates='metrics')