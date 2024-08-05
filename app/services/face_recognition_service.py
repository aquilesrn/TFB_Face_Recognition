import requests
import json
import base64
import boto3

class FaceRecognitionService:
    @staticmethod
    def identify_faces(file, model="Facenet512", metric="euclidean", backend="opencv"):
        files = {'file': file.file}
        data = {'model': model, 'metric': metric, 'backend': backend}
        response = requests.post("http://deepface:5000/verify", files=files, data=data)
        return response.json()

    @staticmethod
    def analyze_face(file, model="DeepFace", backend="retinaface", metric="euclidean"):
        img_content = file.file.read()
        img_base64 = base64.b64encode(img_content).decode('utf-8')
        
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
        
        return response.json()

    @staticmethod
    def analyze_face_rekognition(file, bucket, region='eu-west-1'):
        session = boto3.Session()
        client = session.client('rekognition', region_name=region)

        response = client.detect_faces(
            Image={'Bytes': file.file.read()},
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
        
        return results