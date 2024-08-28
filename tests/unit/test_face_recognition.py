import pytest
from unittest.mock import patch, MagicMock
from app.services.face_recognition_service import FaceRecognitionService
from sqlalchemy.orm import Session
from io import BytesIO

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

def test_identify_faces(mock_db_session):
    mock_file = MagicMock()
    mock_file.file = BytesIO(b"fake_image_data")

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"result": "mocked_result"}
        response = FaceRecognitionService.identify_faces(mock_file, db=mock_db_session)
    
    assert response == {"result": "mocked_result"}
    mock_post.assert_called_once()

def test_analyze_face(mock_db_session):
    mock_file = MagicMock()
    mock_file.file = BytesIO(b"fake_image_data")
    mock_file.filename = "test.jpg"

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"analysis": {"age": 25, "gender": "male"}}
        response = FaceRecognitionService.analyze_face(mock_file, db=mock_db_session)

    assert response == {"analysis": {"age": 25, "gender": "male"}}
    mock_post.assert_called_once()

def test_analyze_face_rekognition(mock_db_session):
    mock_file = MagicMock()
    mock_file.file = BytesIO(b"fake_image_data")

    with patch("boto3.Session.client") as mock_client:
        mock_client.return_value.detect_faces.return_value = {
            "FaceDetails": [{"AgeRange": {"High": 30}, "Gender": {"Value": "Male"}, "Emotions": {"HAPPY": 90.0}}]
        }
        response = FaceRecognitionService.analyze_face_rekognition(mock_file, bucket="test-bucket", db=mock_db_session)
    
    assert len(response) == 1
    assert response[0]["age_range"]["High"] == 30
    assert response[0]["gender"] == "Male"
    assert "HAPPY" in response[0]["emotions"]
    mock_client.assert_called_once()

def test_save_analysis_to_db(mock_db_session):
    mock_results = [{"age": 25, "dominant_emotion": "happy", "dominant_gender": "male"}]
    mock_file_path = "test.jpg"
    mock_model_name = "DeepFace"

    FaceRecognitionService.save_analysis_to_db(mock_db_session, mock_file_path, mock_model_name, {"analysis": {"results": mock_results}})
    
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called()
