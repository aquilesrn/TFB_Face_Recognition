from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.services.face_recognition_service import FaceRecognitionService
from app.database import get_db
import os
import json
import csv
import zipfile
from io import StringIO, BytesIO
from collections import defaultdict

class FaceRecognitionTestsRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.post("/face_recognition_tests/")(self.face_recognition_tests)

    async def face_recognition_tests(self, db: Session = Depends(get_db), folder: UploadFile = File(...)):
        if not folder.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Folder must be a .zip file")

        emotions = ["angry", "disgusted", "fearful", "happy", "neutral", "sad", "surprised"]
        models = ["DeepFace", "Amazon Rekognition"]
        results = defaultdict(lambda: defaultdict(lambda: {"TP": 0, "TN": 0, "FP": 0, "FN": 0}))
        summary = defaultdict(lambda: defaultdict(int))

        total_images = 0
        processed_images = 0

        try:
            folder_content = await folder.read()
            with zipfile.ZipFile(BytesIO(folder_content)) as zip_ref:
                zip_ref.extractall("/tmp/face_recognition_tests")

            for emotion in emotions:
                emotion_path = os.path.join("/tmp/face_recognition_tests", emotion)
                if os.path.exists(emotion_path):
                    total_images += len(os.listdir(emotion_path))

            if total_images == 0:
                raise HTTPException(status_code=400, detail="No images found in the provided directory.")

            async def analysis_generator():
                nonlocal processed_images
                for emotion in emotions:
                    emotion_path = os.path.join("/tmp/face_recognition_tests", emotion)
                    if not os.path.exists(emotion_path):
                        continue

                    for image_name in os.listdir(emotion_path):
                        image_path = os.path.join(emotion_path, image_name)
                        try:
                            if os.path.isfile(image_path):
                                with open(image_path, "rb") as img_file:
                                    img_bytes = img_file.read()
                                    if len(img_bytes) == 0:
                                        print(f"Skipping empty image: {image_name}")
                                        continue
                                    file = UploadFile(filename=image_name, file=BytesIO(img_bytes))

                                # Log to help with debugging Rekognition issues
                                print(f"Processing image {image_name} with size {len(img_bytes)} bytes")

                                # Análisis con DeepFace
                                deepface_analysis = FaceRecognitionService.analyze_face(
                                    file=file,
                                    model="DeepFace",
                                    backend="retinaface",
                                    metric="euclidean"
                                )

                                # Análisis con Amazon Rekognition
                                rekog_analysis = FaceRecognitionService.analyze_face_rekognition(
                                    file=file,
                                    bucket="my-bucket",
                                    region="eu-west-1"
                                )

                                # Evaluación de resultados para DeepFace
                                deepface_emotion = self.get_predicted_emotion(deepface_analysis, "DeepFace")
                                if deepface_emotion == emotion:
                                    results["DeepFace"][emotion]["TP"] += 1
                                else:
                                    results["DeepFace"][emotion]["FN"] += 1
                                    if deepface_emotion != "unknown":
                                        results["DeepFace"][deepface_emotion]["FP"] += 1

                                summary["DeepFace"][deepface_emotion] += 1

                                # Evaluación de resultados para Amazon Rekognition
                                rekog_emotion = self.get_predicted_emotion(rekog_analysis, "Amazon Rekognition")
                                if rekog_emotion == emotion:
                                    results["Amazon Rekognition"][emotion]["TP"] += 1
                                else:
                                    results["Amazon Rekognition"][emotion]["FN"] += 1
                                    if rekog_emotion != "unknown":
                                        results["Amazon Rekognition"][rekog_emotion]["FP"] += 1

                                summary["Amazon Rekognition"][rekog_emotion] += 1

                                for other_emotion in emotions:
                                    if other_emotion != emotion:
                                        if deepface_emotion != other_emotion:
                                            results["DeepFace"][other_emotion]["TN"] += 1
                                        if rekog_emotion != other_emotion:
                                            results["Amazon Rekognition"][other_emotion]["TN"] += 1

                        except Exception as e:
                            print(f"Error processing image {image_name}: {str(e)}")
                            continue

                        processed_images += 1
                        yield json.dumps({
                            "processed": processed_images,
                            "total": total_images,
                            "results": results,
                            "summary": summary,
                            "emotion_evaluated": emotion,
                            "num_images": total_images
                        }) + '\n'

                csv_data = self.export_results_to_csv(results, emotions, models)
                yield csv_data

            return StreamingResponse(analysis_generator(), media_type="application/json")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")

    def get_predicted_emotion(self, analysis, model_name):
        try:
            if model_name == "DeepFace":
                return analysis.get("analysis", {}).get("results", [{}])[0].get("dominant_emotion", "unknown").lower()
            elif model_name == "Amazon Rekognition":
                if analysis and len(analysis) > 0 and "emotions" in analysis[0]:
                    emotions = analysis[0]["emotions"]
                    if emotions:
                        return max(emotions, key=emotions.get).lower()
        except Exception as e:
            print(f"Error extracting predicted emotion: {e}")
            return "unknown"

    def export_results_to_csv(self, results, emotions, models):
        try:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Model", "Emotion", "TP", "TN", "FP", "FN", "Precision", "Recall", "F1-Score", "Accuracy"])

            for model in models:
                for emotion in emotions:
                    tp = results[model][emotion]["TP"]
                    tn = results[model][emotion]["TN"]
                    fp = results[model][emotion]["FP"]
                    fn = results[model][emotion]["FN"]
                    precision = tp / (tp + fp) if tp + fp > 0 else 0
                    recall = tp / (tp + fn) if tp + fn > 0 else 0
                    f1_score = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
                    accuracy = (tp + tn) / (tp + tn + fp + fn) if tp + tn + fp + fn > 0 else 0
                    writer.writerow([model, emotion, tp, tn, fp, fn, precision, recall, f1_score, accuracy])

            output.seek(0)
            return output.getvalue()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while exporting results: {str(e)}")

face_recognition_tests_router = FaceRecognitionTestsRouter()
router = face_recognition_tests_router.router