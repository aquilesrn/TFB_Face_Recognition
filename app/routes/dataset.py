from fastapi import APIRouter, UploadFile, File
from app.services.dataset_service import DatasetService

class DatasetRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.post("/upload_dataset/")(self.upload_dataset)

    async def upload_dataset(self, file: UploadFile = File(...)):
        status = DatasetService.upload_dataset(file)
        return {"status": status}

dataset_router = DatasetRouter()
router = dataset_router.router