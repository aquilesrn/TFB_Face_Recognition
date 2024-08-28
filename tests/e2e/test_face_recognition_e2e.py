import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_face_analysis_e2e():
    with open("tests/test.jpg", "rb") as img:
        response = client.post(
            "/face_analysis/",
            files={"file": ("test.jpg", img, "image/jpeg")},
            data={
                "main_model": "DeepFace",
                "model": "Facenet512",
                "backend": "retinaface",
                "metric": "euclidean",
            }
        )
    
    assert response.status_code == 200
    assert "analysis" in response.json()
    assert "age" in response.json()["analysis"]["results"][0]
    assert "dominant_emotion" in response.json()["analysis"]["results"][0]
    assert "dominant_gender" in response.json()["analysis"]["results"][0]