import pytest
from unittest.mock import patch, MagicMock
from app.routes.real_time_face import RealTimeFaceRouter
from fastapi import HTTPException

router = RealTimeFaceRouter()

@pytest.fixture
def mock_image_data():
    return RealTimeFaceRouter.ImageData(image="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...")

def test_analyze_emotion_success(mock_image_data):
    with patch("deepface.DeepFace.analyze") as mock_analyze, patch("cv2.CascadeClassifier.detectMultiScale") as mock_detect:
        mock_analyze.return_value = [{"dominant_emotion": "happy"}]
        mock_detect.return_value = [(0, 0, 100, 100)]
        
        response = router.analyze_emotion(mock_image_data)
        
        assert response["emotion"] == "happy"
        mock_analyze.assert_called_once()

def test_analyze_emotion_no_face_detected(mock_image_data):
    with patch("cv2.CascadeClassifier.detectMultiScale") as mock_detect:
        mock_detect.return_value = []
        
        response = router.analyze_emotion(mock_image_data)
        
        assert response["emotion"] == "No face detected"

def test_analyze_emotion_exception(mock_image_data):
    with patch("deepface.DeepFace.analyze", side_effect=Exception("Test Exception")):
        with pytest.raises(HTTPException) as excinfo:
            router.analyze_emotion(mock_image_data)
        
        assert "Test Exception" in str(excinfo.value)
