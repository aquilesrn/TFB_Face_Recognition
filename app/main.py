import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from app.config import Config  
from app.routes.face_recognition import face_recognition_router
from app.routes.real_time_face import real_time_face_router
from app.routes.dataset import dataset_router
from app.routes.reports import report_router
from app.routes.face_recognition_tests import face_recognition_tests_router
from fastapi.staticfiles import StaticFiles

class AppConfig:
    def __init__(self):
        self.DATABASE_URL = f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_SERVER}/{Config.POSTGRES_DB}"
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()
        self.templates = Jinja2Templates(directory="app/templates")

    def create_database(self):
        self.Base.metadata.create_all(bind=self.engine)

    def dispose_engine(self):
        self.engine.dispose()

app_config = AppConfig()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_config.create_database()
    yield
    # Shutdown
    app_config.dispose_engine()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(face_recognition_router.router)
app.include_router(dataset_router.router)
app.include_router(report_router.router)
app.include_router(real_time_face_router.router)
app.include_router(face_recognition_tests_router.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return app_config.templates.TemplateResponse("face_analysis.html", {"request": request})

@app.get("/face_analysis", response_class=HTMLResponse)
async def get_face_analysis(request: Request):
    return app_config.templates.TemplateResponse("face_analysis.html", {"request": request})

@app.get("/face_analysis_grouped", response_class=HTMLResponse)
async def get_face_analysis_grouped(request: Request):
    return app_config.templates.TemplateResponse("face_analysis_grouped.html", {"request": request})

@app.get("/face_analysis_dataset", response_class=HTMLResponse)
async def get_face_analysis_dataset(request: Request):
    return app_config.templates.TemplateResponse("face_analysis_dataset.html", {"request": request})

@app.get("/realtime_face_recognition", response_class=HTMLResponse)
async def get_realtime_face_recognition(request: Request):
    return app_config.templates.TemplateResponse("realtime_face_recognition.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return app_config.templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/face_recognition_tests", response_class=HTMLResponse)
async def get_face_recognition_tests(request: Request):
    return app_config.templates.TemplateResponse("face_recognition_tests.html", {"request": request})

@app.get("/generate_report", response_class=HTMLResponse)
async def get_face_recognition_tests(request: Request):
    return app_config.templates.TemplateResponse("detailed_report.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)