import pytest
from app.services.report_service import ReportService
from app.database import SessionLocal, engine
from app.models.models import Image, Model, Analysis, Metric

@pytest.fixture(scope="module")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def test_generate_report_integration(db_session):
    # Crear datos simulados
    new_image = Image(file_path="test_image.jpg")
    new_model = Model(name="Test Model", description="A model for testing")
    db_session.add(new_image)
    db_session.add(new_model)
    db_session.commit()
    db_session.refresh(new_image)
    db_session.refresh(new_model)

    new_analysis = Analysis(image_id=new_image.image_id, model_id=new_model.model_id, result_data={})
    db_session.add(new_analysis)
    db_session.commit()
    db_session.refresh(new_analysis)

    new_metric = Metric(analysis_id=new_analysis.analysis_id, metric_name="dominant_emotion", value="happy")
    db_session.add(new_metric)
    db_session.commit()

    # Generar reporte
    summary_data = ReportService.generate_report(db_session)

    assert len(summary_data) > 0
    assert summary_data[0]["most_repeated_emotion"] == "happy"

def test_generate_detailed_report_integration(db_session):
    # Generar reporte detallado
    detailed_data = ReportService.generate_detailed_report(db_session)

    assert len(detailed_data) > 0
    assert detailed_data[0]["image"] == "test_image.jpg"
    assert detailed_data[0]["emotion"] == "happy"