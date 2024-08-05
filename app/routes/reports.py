from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.services.report_service import ReportService

class ReportRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.get("/generate_report/")(self.generate_report)
        self.router.get("/detailed_report/")(self.detailed_report)
        self.templates = Jinja2Templates(directory="app/templates")

    async def generate_report(self, request: Request):
        report_data = ReportService.generate_report()
        return self.templates.TemplateResponse("report.html", {"request": request, "report": report_data})

    async def detailed_report(self, request: Request):
        detailed_report_data = ReportService.generate_detailed_report()
        return self.templates.TemplateResponse("detailed_report.html", {"request": request, "report": detailed_report_data})

report_router = ReportRouter()
router = report_router.router