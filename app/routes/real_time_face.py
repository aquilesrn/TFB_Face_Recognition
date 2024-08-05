from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import base64
from deepface import DeepFace

class RealTimeFaceRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.post("/analyze_emotion/")(self.analyze_emotion)

    class ImageData(BaseModel):
        image: str

    async def analyze_emotion(self, data: ImageData):
        try:
            # Decodificar la imagen de base64 a numpy array
            img_data = base64.b64decode(data.image.split(",")[1])
            np_img = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            # Convertir la imagen a escala de grises
            gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Cargar el clasificador de cascada frontal
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detectar caras en la imagen
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) == 0:
                return {"emotion": "No face detected"}

            # Asumir que hay solo una cara en el frame y tomar la primera
            (x, y, w, h) = faces[0]
            face_roi = img[y:y + h, x:x + w]

            # Analizar la emoción en la región de interés
            result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']

            return {"emotion": emotion}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

real_time_face_router = RealTimeFaceRouter()
router = real_time_face_router.router