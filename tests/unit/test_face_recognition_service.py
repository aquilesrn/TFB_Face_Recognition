import pytest
from unittest.mock import patch, MagicMock
from app.services.face_recognition_service import FaceRecognitionService
from io import BytesIO

@pytest.fixture
def mock_file():
    file = MagicMock()
    file.file = BytesIO(b"fake_image_data")
    file.filename = "test.jpg"
    return file

def test_find_faces(mock_file):
    with patch("deepface.DeepFace.find") as mock_find:
        mock_find.return_value = [
            {"facial_area": {"x": 0, "y": 0, "w": 100, "h": 100}, "identity": "Person A", "distance": 0.3}
        ]
        response = FaceRecognitionService.find_faces(mock_file, db_path="test_db")
    
    assert len(response) == 1
    assert response[0]["identity"] == "Person A"
    mock_find.assert_called_once()

def test_save_analysis_to_db(mock_file, mock_db_session):
    mock_analysis_results = {"results": [{"age": 30, "gender": "male", "emotion": "happy"}]}
    
    FaceRecognitionService.save_analysis_to_db(mock_db_session, "test_image.jpg", "DeepFace", {"analysis": mock_analysis_results})
    
    assert mock_db_session.add.called
    assert mock_db_session.commit.called