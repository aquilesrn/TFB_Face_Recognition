from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.face_recognition_service import FaceRecognitionService
import os
import zipfile
import json

class FaceRecognitionRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.post("/face_analysis/")(self.face_analysis)
        self.router.post("/face_analysis_dataset/")(self.face_analysis_dataset)

    async def face_analysis(self, file: UploadFile = File(...), main_model: str = Form(...), model: str = Form(...), backend: str = Form("retinaface"), metric: str = Form("euclidean"), region: str = Form("us-east-1"), bucket: str = Form("my-bucket")):
        if main_model == "DeepFace":
            analysis = FaceRecognitionService.analyze_face(file, model=model, backend=backend, metric=metric)
        elif main_model == "Amazon Rekognition":
            analysis = FaceRecognitionService.analyze_face_rekognition(file, bucket=bucket, region=region)
        else:
            analysis = {"error": "Modelo no reconocido"}
        return {"analysis": analysis}

    async def face_analysis_dataset(self, folder: UploadFile = File(...), main_model: str = Form(...), model: str = Form(...), backend: str = Form("retinaface"), metric: str = Form("euclidean")):
        if main_model != "DeepFace":
            return JSONResponse(content={"error": "Modelo no reconocido o no implementado"}, status_code=400)
        
        if not folder.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Folder must be a .zip file")

        # Save uploaded zip file
        folder_path = f"/tmp/{folder.filename}"
        with open(folder_path, "wb") as f:
            f.write(folder.file.read())

        # Extract zip file
        with zipfile.ZipFile(folder_path, 'r') as zip_ref:
            zip_ref.extractall("/tmp")

        extracted_folder = folder_path.replace(".zip", "")
        
        # Count images in the folder
        image_extensions = ('.png', '.jpg', '.jpeg')
        total_images = sum(
            1 for root, dirs, files in os.walk(extracted_folder)
            for file in files if file.lower().endswith(image_extensions)
        )
        
        async def analysis_generator():
            results = []
            analyzed_images = 0
            for root, dirs, files in os.walk(extracted_folder):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        file_path = os.path.join(root, file)
                        with open(file_path, "rb") as img_file:
                            img = UploadFile(filename=file, file=img_file)
                            analysis = FaceRecognitionService.analyze_face(img, model=model, backend=backend, metric=metric)
                            analyzed_images += 1
                            yield json.dumps({
                                "analyzed": analyzed_images,
                                "total": total_images,
                                "analysis": analysis
                            }) + '\n'
        
        return StreamingResponse(analysis_generator(), media_type="application/json")

face_recognition_router = FaceRecognitionRouter()
router = face_recognition_router.router