from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.services.report_service import ReportService
from app.database import get_db

class ReportRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.get("/detailed_report")(self.generate_report)
        self.templates = Jinja2Templates(directory="app/templates")

    async def generate_report(self, request: Request, db: Session = Depends(get_db)):
        summary_data = ReportService.generate_report(db)
        detailed_data = ReportService.generate_detailed_report(db)
        return self.templates.TemplateResponse("detailed_report.html", {
            "request": request,
            "summary_data": summary_data,
            "analysis_details": detailed_data
        })

report_router = ReportRouter()
router = report_router.router