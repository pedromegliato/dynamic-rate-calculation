"""
Testes para os cálculos de seguro.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from app.domain.value_objects import Money, Percentage, Address, CarInfo
from app.domain.services.insurance_calculator import InsuranceCalculator
from app.domain.exceptions import InvalidCarInfoError

@pytest.fixture
def car_info_entity():
    """Fixture para criar uma entidade CarInfo de teste."""
    return CarInfo(
        make="Toyota",
        model="Corolla",
        year=2020,
        value=Decimal('100000.00')
    )

def test_rate_calculation_by_age(calculator):
    """Testa o cálculo da taxa por idade do carro."""
    # Cálculo com taxas 0.5% (idade/valor) e GIS 4% (SP):
    # Age(5a) = 0.025, Value(100k) = 0.05, GIS = 0.04 -> Total = 0.115
    rate = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 5, 
        car_value=100000.0,
        registration_state="SP"
    )
    assert abs(rate - 0.115) < 0.001 # Esperado 0.115

def test_rate_calculation_by_value(calculator):
    """Testa o cálculo da taxa por valor do carro."""
    # Cálculo esperado: 1 ano -> 0.5% age + 20 * 0.5% = 10% value = 10.5% + 2% GIS = 12.5%
    # Ajuste na regra do teste: Usando 2% para AGE_ADJUSTMENT_RATE e 1% para VALUE_ADJUSTMENT_RATE (conftest.py)
    # 1 ano * 2% = 2% age
    # 20 * 1% = 20% value
    # GIS (SP) = 4% (conftest.py)
    # Total = 2% + 20% + 4% = 26%
    rate = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 1,
        car_value=200000.0,
        registration_state="SP"
    )
    assert abs(rate - 0.145) < 0.001

def test_premium_calculation(calculator):
    """Testa o cálculo do prêmio."""
    # Prêmio final = Base Premium - Deductible Discount + Broker's Fee
    # Base Premium = car value * applied rate
    # Deductible Discount = base premium * deductible percentage
    # Exemplo: 150k * 7% = 10500 (Base) -> Disc = 10500 * 10% = 1050 -> Final = 10500 - 1050 + 500 = 9950
    premium = calculator.calculate_premium_alt(
        car_value=150000.0,
        rate=0.07,
        deductible_percentage=0.10,
        broker_fee=500.0
    )
    assert abs(premium - 9950.0) < 0.01

def test_premium_calculation_with_different_deductibles(calculator):
    """Testa o cálculo do prêmio com diferentes franquias."""
    # Exemplo 1 (5%): 100k * 7% = 7000 -> Disc = 7000 * 5% = 350 -> Final = 7000 - 350 + 500 = 7150
    premium_min = calculator.calculate_premium_alt(
        car_value=100000.0,
        rate=0.07,
        deductible_percentage=0.05,
        broker_fee=500.0
    )
    assert abs(premium_min - 7150.0) < 0.01
    
    # Exemplo 2 (15%): 100k * 7% = 7000 -> Disc = 7000 * 15% = 1050 -> Final = 7000 - 1050 + 500 = 6450
    premium_max = calculator.calculate_premium_alt(
        car_value=100000.0,
        rate=0.07,
        deductible_percentage=0.15,
        broker_fee=500.0
    )
    assert abs(premium_max - 6450.0) < 0.01

def test_policy_limit_calculation(calculator):
    """Testa o cálculo do limite da apólice."""
    # Final Policy Limit = Base Policy Limit - Deductible Value
    # Base Policy Limit = car value * coverage percentage (default 100%)
    # Deductible Value = base policy limit * deductible percentage
    # Exemplo: Base = 100k * 1 = 100k -> Ded Val = 100k * 10% = 10k -> Final = 100k - 10k = 90k
    limit = calculator.calculate_policy_limit_alt(
        car_value=100000.0,
        deductible_percentage=0.10
    )
    assert abs(limit - 90000.0) < 0.01

def test_gis_adjustment(calculator):
    """Testa o ajuste GIS por estado, alinhado com as taxas de teste."""
    # Usar taxas 0.5% (idade/valor) e GIS 4% (SP) de conftest
    # Carro de 1 ano, 100k:
    # Com SP: (1*0.005) + (100/10 * 0.005) + 0.04 = 0.005 + 0.05 + 0.04 = 0.095
    rate_sp = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 1, # 1 ano
        car_value=100000.0,
        registration_state="SP"
    )
    assert abs(rate_sp - 0.095) < 0.001 # Esperado 0.095
    
    # Sem localização: (1*0.005) + (100/10 * 0.005) = 0.055
    rate_no_location = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 1, # 1 ano
        car_value=100000.0,
        registration_state=None
    )
    assert abs(rate_no_location - 0.055) < 0.001 # Esperado 0.055
    assert rate_sp > rate_no_location 