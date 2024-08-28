import pytest
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models.models import Image, Model, Analysis

@pytest.fixture(scope="module")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def test_create_and_read_image(db_session):
    # Crear un nuevo registro en la tabla Image
    new_image = Image(file_path="test_image.jpg")
    db_session.add(new_image)
    db_session.commit()
    db_session.refresh(new_image)
    
    # Leer el registro y verificar que se guardó correctamente
    image_from_db = db_session.query(Image).filter_by(file_path="test_image.jpg").first()
    assert image_from_db is not None
    assert image_from_db.file_path == "test_image.jpg"

def test_update_model(db_session):
    # Crear un nuevo modelo
    new_model = Model(name="Test Model", description="A model for testing")
    db_session.add(new_model)
    db_session.commit()
    db_session.refresh(new_model)

    # Actualizar el modelo
    new_model.description = "Updated description"
    db_session.commit()

    # Verificar que la actualización se realizó correctamente
    model_from_db = db_session.query(Model).filter_by(name="Test Model").first()
    assert model_from_db.description == "Updated description"

def test_delete_analysis(db_session):
    # Crear un nuevo análisis
    new_analysis = Analysis(image_id=1, model_id=1, result_data={"result": "test"})
    db_session.add(new_analysis)
    db_session.commit()
    db_session.refresh(new_analysis)

    # Borrar el análisis
    db_session.delete(new_analysis)
    db_session.commit()

    # Verificar que se eliminó correctamente
    analysis_from_db = db_session.query(Analysis).filter_by(analysis_id=new_analysis.analysis_id).first()
    assert analysis_from_db is None