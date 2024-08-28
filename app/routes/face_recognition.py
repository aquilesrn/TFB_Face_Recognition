from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from app.services.face_recognition_service import FaceRecognitionService
from app.database import get_db
import os
import zipfile
import json
from io import BytesIO

class FaceRecognitionRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.post("/face_analysis/")(self.face_analysis)
        self.router.post("/face_analysis_dataset/")(self.face_analysis_dataset)
        self.router.post("/face_analysis_grouped/")(self.face_analysis_grouped)  # Nuevo endpoint

    async def face_analysis(self, db: Session = Depends(get_db), file: UploadFile = File(...), main_model: str = Form(...), model: str = Form(...), backend: str = Form("retinaface"), metric: str = Form("euclidean"), region: str = Form("us-east-1"), bucket: str = Form("my-bucket")):
        analysis = None
        file_path = f"/uploads/{file.filename}"  # Ruta donde se guardará la imagen (esto es solo un ejemplo)

        if main_model == "DeepFace":
            analysis = FaceRecognitionService.analyze_face(file, model=model, backend=backend, metric=metric, db=db)
        elif main_model == "Amazon Rekognition":
            analysis = FaceRecognitionService.analyze_face_rekognition(file, bucket=bucket, region=region,db=db)
        else:
            analysis = {"error": "Modelo no reconocido"}
        
        return {"analysis": analysis}

    async def face_analysis_dataset(self,db: Session = Depends(get_db), folder: UploadFile = File(...), main_model: str = Form(...), model: str = Form(...), backend: str = Form("retinaface"), metric: str = Form("euclidean"), region: str = Form("us-east-1"), bucket: str = Form("my-bucket")):
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
            analyzed_images = 0
            for root, dirs, files in os.walk(extracted_folder):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        file_path = os.path.join(root, file)
                        with open(file_path, "rb") as img_file:
                            img_bytes = img_file.read()
                            if len(img_bytes) == 0:
                                print(f"Skipping empty image: {file}")
                                continue
                            upload_file = UploadFile(filename=file, file=BytesIO(img_bytes))

                            if main_model == "DeepFace":
                                analysis = FaceRecognitionService.analyze_face(upload_file, model=model, backend=backend, metric=metric, db=db)
                            elif main_model == "Amazon Rekognition":
                                # Use the same method as face_analysis to process image for Rekognition
                                upload_file.file.seek(0)  # Ensure the file pointer is at the start
                                analysis = FaceRecognitionService.analyze_face_rekognition(upload_file, bucket=bucket, region=region,db=db)
                            else:
                                analysis = {"error": "Modelo no reconocido"}

                            # Check if analysis returned valid results
                            if analysis:
                                if main_model == "DeepFace" and "results" in analysis.get("analysis", {}):
                                    face_data = analysis["analysis"]["results"][0]
                                    yield json.dumps({
                                        "analyzed": analyzed_images,
                                        "total": total_images,
                                        "analysis": {
                                            "age": face_data.get("age"),
                                            "dominant_emotion": face_data.get("dominant_emotion"),
                                            "dominant_gender": face_data.get("dominant_gender"),
                                            "dominant_race": face_data.get("dominant_race")
                                        }
                                    }) + '\n'
                                elif main_model == "Amazon Rekognition" and len(analysis) > 0:
                                    face_data = analysis[0]
                                    yield json.dumps({
                                        "analyzed": analyzed_images,
                                        "total": total_images,
                                        "analysis": {
                                            "age": face_data.get("age_range", {}).get("High"),
                                            "dominant_emotion": max(face_data.get("emotions", {}), key=face_data.get("emotions", {}).get),
                                            "dominant_gender": face_data.get("gender"),
                                            "dominant_race": "N/A"  # Amazon Rekognition doesn't return race data
                                        }
                                    }) + '\n'

                            analyzed_images += 1

        return StreamingResponse(analysis_generator(), media_type="application/json")

    async def face_analysis_grouped(self,db: Session = Depends(get_db), file: UploadFile = File(...), main_model: str = Form(...), model: str = Form(...), backend: str = Form("retinaface"), metric: str = Form("euclidean"), region: str = Form("us-east-1"), bucket: str = Form("my-bucket")):
        if main_model == "DeepFace":
            analysis = FaceRecognitionService.analyze_face(file, model=model, backend=backend, metric=metric,db=db)
        elif main_model == "Amazon Rekognition":
            analysis = FaceRecognitionService.analyze_face_rekognition(file, bucket=bucket, region=region,db=db)
        else:
            analysis = {"error": "Modelo no reconocido"}
        return {"analysis": analysis}

face_recognition_router = FaceRecognitionRouter()
router = face_recognition_router.router