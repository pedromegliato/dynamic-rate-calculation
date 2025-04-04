"""
Configurações para os testes.
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app, get_insurance_repository
from app.domain.value_objects import Money, Percentage, Address, CarInfo
from app.domain.services.insurance_calculator import InsuranceCalculator
from pydantic import BaseModel, Field, ConfigDict
from app.domain.entities import InsuranceCalculationEntity
from app.domain.interfaces.repository import InsuranceCalculationRepository
from typing import Dict
from datetime import datetime

# Definir o modo de teste
app.state.testing = True

# Fixtures Globais 

@pytest.fixture(scope="session")
def test_settings():
    """Fixture para fornecer configurações de teste consistentes."""
    class TestInsuranceConfigForTesting(BaseModel):
        BASE_RATE: Decimal = Decimal('0.05')
        MIN_CAR_YEAR: int = 2000
        MAX_CAR_VALUE: Decimal = Decimal('500000.0')
        AGE_ADJUSTMENT_RATE: Decimal = Decimal('0.005')
        VALUE_ADJUSTMENT_RATE: Decimal = Decimal('0.005')
        MIN_DEDUCTIBLE_PERCENTAGE: Decimal = Decimal('0.05')
        MAX_DEDUCTIBLE_PERCENTAGE: Decimal = Decimal('0.15')
        MIN_BROKER_FEE: Decimal = Decimal('0.05')
        MAX_BROKER_FEE: Decimal = Decimal('0.15')
        COVERAGE_PERCENTAGE: Decimal = Decimal('1.0')
        GIS_ADJUSTMENT_RATE: Dict[str, Decimal] = {
            "SP": Decimal('0.04'),
            "RJ": Decimal('0.03'),
        }
        model_config = ConfigDict(extra='ignore')

    class TestSettingsForTesting(BaseModel):
        INSURANCE: TestInsuranceConfigForTesting = TestInsuranceConfigForTesting()
        
        class RetryConfigForTesting(BaseModel):
             MAX_RETRIES: int = 1
             RETRY_DELAY: int = 0
             model_config = ConfigDict(extra='ignore')
        RETRY: RetryConfigForTesting = RetryConfigForTesting()

        class APIConfigForTesting(BaseModel):
             TITLE: str = "Test API"
             DESCRIPTION: str = "API for testing"
             VERSION: str = "0.0.test"
             model_config = ConfigDict(extra='ignore')
        API: APIConfigForTesting = APIConfigForTesting()
        
        ENVIRONMENT: str = "testing"
        
        model_config = ConfigDict(extra='ignore')

    return TestSettingsForTesting()

@pytest.fixture
def calculator(test_settings):
    """Fixture para criar um InsuranceCalculator com settings de teste."""
    return InsuranceCalculator(test_settings)

@pytest.fixture
def client():
    """Fixture para criar um cliente de teste FastAPI."""
    return TestClient(app)

@pytest.fixture
def mock_repository():
    """Fixture para criar um repositório mockado."""
    repo = Mock(spec=InsuranceCalculationRepository)
    repo.save_calculation = AsyncMock(return_value=None)
    repo.get_calculation = AsyncMock(return_value=None)
    repo.list_calculations = AsyncMock(return_value=[])
    return repo

@pytest.fixture(autouse=True)
def override_repository_dependency(mock_repository):
    """Sobrescreve a dependência get_insurance_repository para usar o mock."""
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_insurance_repository] = lambda: mock_repository
    yield
    app.dependency_overrides = original_overrides

@pytest.fixture
def car_info_vo():
    """Fixture para criar um Value Object CarInfo."""
    return CarInfo(make="Toyota", model="Corolla", year=2020, value=Decimal('100000.00'))

@pytest.fixture
def settings(test_settings):
    return test_settings 