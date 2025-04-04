"""
Testes para os endpoints da API.
"""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.application.dtos.insurance import InsuranceCalculationRequest, InsuranceCalculationResponse
from app.domain.value_objects import Address
from unittest.mock import patch, AsyncMock
from app.domain.entities import InsuranceCalculationEntity
from app.domain.value_objects import Money, Percentage, CarInfo
from datetime import datetime, UTC

client = TestClient(app)

@pytest.fixture
def valid_calculation_request_data():
    """Retorna dados válidos para a requisição de cálculo."""
    return {
        "make": "Volkswagen",
        "model": "Golf",
        "year": 2021,
        "value": 120000.0,
        "deductible_percentage": 0.10,
        "broker_fee": 600.0
    }

@pytest.fixture
def valid_calculation_request_data_with_location():
    """Retorna dados válidos com localização."""
    return {
        "make": "Honda",
        "model": "Civic",
        "year": 2019,
        "value": 95000.0,
        "deductible_percentage": 0.08,
        "broker_fee": 450.0,
        "registration_location": {
            "street": "Av. Paulista",
            "number": "1000",
            "complement": "Andar 10",
            "neighborhood": "Bela Vista",
            "city": "São Paulo",
            "state": "SP",
            "postal_code": "01310-100",
            "country": "BR"
        }
    }

@pytest.fixture
def mock_use_case_result():
    """Retorna um resultado mockado do caso de uso."""
    # Simular a entidade que o caso de uso retornaria
    return InsuranceCalculationEntity(
        id="test-uuid-123",
        car_info=CarInfo(make="MockMake", model="MockModel", year=2022, value=Decimal("50000")),
        applied_rate=Decimal("0.06"), 
        calculated_premium=Money(amount=Decimal("2800")),
        deductible_value=Money(amount=Decimal("5000")),
        policy_limit=Money(amount=Decimal("45000")),
        broker_fee=Money(amount=Decimal("300")),
        gis_adjustment=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )

def test_calculate_insurance_success(valid_calculation_request_data, mock_use_case_result):
    """Testa o endpoint de cálculo com sucesso."""
    # Mockar o método execute do CalculateInsuranceUseCase
    with patch('app.application.use_cases.calculate_insurance.CalculateInsuranceUseCase.execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = mock_use_case_result
        
        response = client.post("/insurance/calculate", json=valid_calculation_request_data)
        
        assert response.status_code == 201
        expected_call_args = valid_calculation_request_data.copy()
        expected_call_args['registration_location'] = None
        mock_execute.assert_called_once_with(**expected_call_args)
        
        response_data = response.json()
        parsed_response = InsuranceCalculationResponse(**response_data)
        assert parsed_response.id == mock_use_case_result.id
        assert parsed_response.car_make == mock_use_case_result.car_info.make
        assert abs(parsed_response.calculated_premium - float(mock_use_case_result.calculated_premium.amount)) < 0.01

def test_calculate_insurance_invalid_data():
    """Testa o endpoint de cálculo com dados inválidos (ex: ano futuro)."""
    invalid_data = {
        "make": "Test",
        "model": "Invalid",
        "year": datetime.now().year + 2,
        "value": 50000.0,
        "deductible_percentage": 0.1,
        "broker_fee": 100.0
    }
    response = client.post("/insurance/calculate", json=invalid_data)
    assert response.status_code == 422

def test_calculate_insurance_use_case_error(valid_calculation_request_data):
    """Testa o endpoint quando o caso de uso lança uma exceção."""
    with patch('app.application.use_cases.calculate_insurance.CalculateInsuranceUseCase.execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.side_effect = Exception("Erro simulado no caso de uso")
        
        response = client.post("/insurance/calculate", json=valid_calculation_request_data)
        
        assert response.status_code == 500
        assert "Erro interno inesperado ao calcular o seguro" in response.json()["detail"]

def test_health_check():
    """Testa o endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data

def test_metrics():
    """Testa o endpoint de métricas."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "disk_percent" in data 