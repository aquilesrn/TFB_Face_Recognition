import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_report_e2e():
    response = client.get("/detailed_report")
    
    assert response.status_code == 200
    assert "Summary Report" in response.text  # Verificar que el reporte contiene el título esperado
    assert "Detailed Report" in response.text  # Verificar que el reporte contiene el título esperado

def test_generate_report_data_e2e():
    response = client.get("/detailed_report")
    
    assert response.status_code == 200
    assert "summary_data" in response.text  # Verificar que los datos del resumen están presentes
    assert "analysis_details" in response.text  # Verificar que los detalles del análisis están presentes