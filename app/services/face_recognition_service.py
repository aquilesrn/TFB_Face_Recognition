import requests
import json
import base64
import boto3 
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy.orm import Session
from app.models.models import Image, Analysis, Metric, Model
import numpy as np
import cv2
from deepface import DeepFace

class FaceRecognitionService:
    @staticmethod
    def identify_faces(file, model="Facenet512", metric="euclidean", backend="opencv", db: Session = None):
        files = {'file': file.file}
        data = {'model': model, 'metric': metric, 'backend': backend}
        response = requests.post("http://deepface:5000/verify", files=files, data=data)
        
        analysis_results = response.json()
        # Guardar los resultados en la base de datos
        if db is not None:
            FaceRecognitionService.save_analysis_to_db(db, file.filename, model, analysis_results)

        
        return response.json()

    @staticmethod
    def analyze_face(file, model="DeepFace", backend="retinaface", metric="euclidean", db: Session = None):
        img_content = file.file.read()
        img_extension = file.filename.split('.')[-1].lower()
        img_base64 = base64.b64encode(img_content).decode('utf-8')
        
        if img_extension == 'png':
            mime_type = "data:image/png;base64"
        else:
            mime_type = "data:image/jpeg;base64"
        
        data = {
            "img_path": f"data:image/jpeg;base64,{img_base64}",
            "actions": ["age", "gender", "emotion", "race"]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(
            "http://deepface:5000/analyze",
            headers=headers,
            data=json.dumps(data)
        )
        
        analysis_results = response.json()

        # Guardar los resultados en la base de datos
        if db is not None:
            FaceRecognitionService.save_analysis_to_db(db, file.filename, model, analysis_results)
        
        
        return response.json()

    @staticmethod
    def find_faces(file, db_path, model="VGG-Face", backend="opencv", distance_metric="cosine"):
        img_content = file.file.read()
        img_array = np.frombuffer(img_content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Ejecución del análisis usando DeepFace
        df = DeepFace.find(
            img_path=img,
            db_path=db_path,
            model_name=model,
            distance_metric=distance_metric,
            detector_backend=backend,
            enforce_detection=False
        )

        # Si se encuentran caras, extraer las coordenadas del bounding box
        results = []
        if len(df) > 0:
            for index, row in df.iterrows():
                bounding_box = row['facial_area']
                result = {
                    "bounding_box": {
                        "x": bounding_box['x'],
                        "y": bounding_box['y'],
                        "w": bounding_box['w'],
                        "h": bounding_box['h']
                    },
                    "identity": row['identity'],
                    "distance": row['distance'],
                    "model": model
                }
                results.append(result)

        return results

    @staticmethod
    def analyze_face_rekognition(file, bucket, region='eu-west-1', db: Session = None):
        # session = boto3.Session()
        session = boto3.Session(
            aws_access_key_id='##########',
            aws_secret_access_key='#########/##############',
            region_name=region
        )
        client = session.client('rekognition', region_name=region)
        try:
        
            im = file.file.read()
            response = client.detect_faces(
                Image={'Bytes': im},
                Attributes=['ALL']
            )
            
            results = []
            for face_detail in response['FaceDetails']:
                face_data = {
                    "age_range": face_detail['AgeRange'],
                    "gender": face_detail['Gender']['Value'],
                    "emotions": {emotion['Type']: emotion['Confidence'] for emotion in face_detail['Emotions']},
                    "face_confidence": face_detail['Confidence'],
                    "bounding_box": face_detail['BoundingBox']
                }
                results.append(face_data)
        
            # Guardar los resultados en la base de datos
            if db is not None:
                FaceRecognitionService.save_analysis_to_db(db, file.filename, "Amazon Rekognition", results)

            return results
        except (BotoCoreError, ClientError) as error:
            print(f"Error calling Rekognition: {error}")
            return []

    @staticmethod
    def save_analysis_to_db(db: Session, file_path: str, model_name: str, analysis_results: dict):
        # Crear y almacenar el registro de la imagen
        new_image = Image(file_path=file_path)
        db.add(new_image)
        db.commit()
        db.refresh(new_image)

        if model_name == "DeepFace":
            # DeepFace devuelve los resultados en una estructura anidada bajo "analysis" -> "results"
            results = analysis_results.get("analysis", {}).get("results", [])
        else:
            # Para Amazon Rekognition, el resultado es directamente una lista
            results = analysis_results

        for result in results:  # Iterar sobre cada resultado en la lista
            # Verificar que result es un diccionario
            if not isinstance(result, dict):
                continue

            # Crear y almacenar el registro de análisis
            model = db.query(Model).filter(Model.name == model_name).first()
            if not model:
                model = Model(name=model_name, description=f"Analysis from {model_name}")
                db.add(model)
                db.commit()
                db.refresh(model)

            new_analysis = Analysis(image_id=new_image.image_id, model_id=model.model_id, result_data=result)
            db.add(new_analysis)
            db.commit()
            db.refresh(new_analysis)

            # Procesar y almacenar las métricas según el modelo
            if model_name == "DeepFace":
                # Guardar las métricas principales para DeepFace
                age = result.get("age")
                dominant_emotion = result.get("dominant_emotion")
                dominant_gender = result.get("dominant_gender")
                dominant_race = result.get("dominant_race")

                if age is not None:
                    new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="age", value=str(age))
                    db.add(new_metric)

                if dominant_emotion:
                    new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="dominant_emotion", value=dominant_emotion)
                    db.add(new_metric)

                if dominant_gender:
                    new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="dominant_gender", value=dominant_gender)
                    db.add(new_metric)

                if dominant_race:
                    new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="dominant_race", value=dominant_race)
                    db.add(new_metric)

            elif model_name == "Amazon Rekognition":
                # Guardar las métricas principales para Amazon Rekognition
                age_range = result.get("age_range")
                gender = result.get("gender")
                emotions = result.get("emotions", {})

                if age_range:
                    high_age = age_range.get("High")
                    if high_age is not None:
                        new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="age_range_high", value=str(high_age))
                        db.add(new_metric)

                if gender:
                    new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="gender", value=gender)
                    db.add(new_metric)

                # Obtener la emoción dominante
                if emotions:
                    dominant_emotion = max(emotions, key=emotions.get)
                    new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="dominant_emotion", value=dominant_emotion)
                    db.add(new_metric)

            db.commit()
