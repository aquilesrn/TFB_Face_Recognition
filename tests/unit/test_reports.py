import pytest
from unittest.mock import MagicMock
from app.services.report_service import ReportService
from sqlalchemy.orm import Session

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

def test_generate_report(mock_db_session):
    mock_db_session.query.return_value.join.return_value.filter.return_value.group_by.return_value.all.return_value = [
        {"date": "2024-08-25", "model": "Amazon Rekognition", "total_analysis": 20, "most_repeated_emotion": "HAPPY", "most_repeated_gender": "Female"}
    ]
    
    result = ReportService.generate_report(mock_db_session)
    
    assert len(result) == 1
    assert result[0]["most_repeated_emotion"] == "HAPPY"

def test_generate_detailed_report(mock_db_session):
    mock_db_session.query.return_value.join.return_value.group_by.return_value.all.return_value = [
        {"date": "2024-08-25", "image": "img1.jpg", "model": "Amazon Rekognition", "age": "30", "gender": "Male", "emotion": "HAPPY"}
    ]
    
    result = ReportService.generate_detailed_report(mock_db_session)
    
    assert len(result) == 1
    assert result[0]["age"] == "30"