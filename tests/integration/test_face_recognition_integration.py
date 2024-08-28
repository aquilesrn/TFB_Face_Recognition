import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from app.services.face_recognition_service import FaceRecognitionService
from app.database import SessionLocal, engine
from app.models.models import Image, Analysis

@pytest.fixture(scope="module")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def mock_file():
    file = MagicMock()
    file.file = BytesIO(b"fake_image_data")
    file.filename = "test.jpg"
    return file

def test_analyze_face_and_save_to_db(db_session, mock_file):
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "analysis": {
                "results": [{"age": 30, "dominant_emotion": "happy", "dominant_gender": "male"}]
            }
        }

        analysis_results = FaceRecognitionService.analyze_face(mock_file, db=db_session)

        # Verificar que los resultados del análisis se guardaron en la base de datos
        image_from_db = db_session.query(Image).filter_by(file_path="test.jpg").first()
        assert image_from_db is not None

        analysis_from_db = db_session.query(Analysis).filter_by(image_id=image_from_db.image_id).first()
        assert analysis_from_db is not None
        assert analysis_from_db.result_data['dominant_emotion'] == "happy"