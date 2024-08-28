import pytest
from fastapi.testclient import TestClient
from io import BytesIO
import zipfile
from app.main import app

client = TestClient(app)

def test_face_analysis_dataset_e2e():
    # Crear un archivo zip en memoria que contiene una imagen de prueba
    img_data = BytesIO()
    with zipfile.ZipFile(img_data, 'w') as zip_file:
        with open("tests/test.jpg", "rb") as img:
            zip_file.writestr("test.jpg", img.read())

    img_data.seek(0)

    # Enviar el archivo zip como parte de la solicitud
    response = client.post(
        "/face_analysis_dataset/",
        files={"folder": ("test.zip", img_data, "application/zip")},
        data={
            "main_model": "DeepFace",
            "model": "Facenet512",
            "backend": "retinaface",
            "metric": "euclidean",
        }
    )
    
    assert response.status_code == 200
    assert response.text.startswith('{"analyzed":')  # Comprobar que la respuesta comienza con lo esperado