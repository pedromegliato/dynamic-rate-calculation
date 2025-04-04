"""
Testes para o calculador de seguros.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from app.domain.value_objects.car_info import CarInfo
from app.domain.value_objects.money import Money
from app.domain.value_objects.percentage import Percentage
from app.domain.value_objects.address import Address
from app.domain.services.insurance_calculator import InsuranceCalculator
from app.domain.exceptions import InvalidCarInfoError
from app.config.settings import Settings
from pydantic import Field

def test_calculate_rate_based_on_age(calculator):
    """Testa o cálculo da taxa baseado na idade do carro."""
    # Usando taxas de conftest.py: AGE_ADJUSTMENT_RATE=0.02, VALUE_ADJUSTMENT_RATE=0.01, GIS_ADJUSTMENT_RATE["SP"]=0.04
    # Carro com 4 anos -> Age Adj = 4 * 0.02 = 0.08
    # Valor 100k -> Value Adj = 100000 / 10000 * 0.01 = 0.10
    # GIS (SP) -> 0.04
    # Total Rate = 0.08 + 0.10 + 0.04 = 0.22
    # Cálculo com taxas 0.5% (idade/valor) e GIS 4% (SP):
    # Age(4a) = 0.02, Value(100k) = 0.05, GIS = 0.04 -> Total = 0.11
    rate = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 4, 
        car_value=100000.0,
        registration_state="SP"
    )
    assert abs(rate - 0.11) < 0.001 # Esperado 0.11

def test_calculate_rate_based_on_value(calculator):
    """Testa o cálculo da taxa baseado no valor do carro."""
    # Usando taxas de conftest.py: AGE=0.02, VALUE=0.01, GIS(SP)=0.04
    # Carro com 1 ano -> Age Adj = 1 * 0.02 = 0.02
    # Valor 200k -> Value Adj = 200000 / 10000 * 0.01 = 0.20
    # GIS (SP) -> 0.04
    # Total Rate = 0.02 + 0.20 + 0.04 = 0.26
    # Cálculo com taxas 0.5% (idade/valor) e GIS 4% (SP):
    # Age(1a) = 0.005, Value(200k) = 0.10, GIS = 0.04 -> Total = 0.145
    rate = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 1, 
        car_value=200000.0,
        registration_state="SP"
    )
    assert abs(rate - 0.145) < 0.001 # Esperado 0.145

def test_calculate_rate_with_gis_adjustment(calculator):
    """Testa o cálculo da taxa com e sem ajuste GIS."""
    # Cálculo com taxas 0.5% (idade/valor) e GIS 4% (SP):
    # Age(1a) = 0.005, Value(200k) = 0.10, GIS = 0.04 -> Total = 0.145
    rate_sp = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 1,
        car_value=200000.0,
        registration_state="SP"
    )
    assert abs(rate_sp - 0.145) < 0.001 # Esperado 0.145

    # Sem localização: Age(1a)=0.005, Value(200k)=0.10 -> Total = 0.105
    rate_no_location = calculator.calculate_rate_alt(
        car_year=datetime.now().year - 1,
        car_value=200000.0,
        registration_state=None
    )
    assert abs(rate_no_location - 0.105) < 0.001 # Esperado 0.105
    assert rate_sp > rate_no_location

def test_calculate_premium_with_deductible_and_broker_fee(calculator):
    """Testa o cálculo do prêmio com franquia e taxa do corretor."""
    # Regra: Final Premium = Base Premium - Deductible Discount + Broker's Fee
    # Base Premium = car value * applied rate
    # Deductible Discount = base premium * deductible percentage
    # Exemplo: 100k, rate 7%, deductible 10%, broker 500
    # Base = 100k * 0.07 = 7000
    # Discount = 7000 * 0.10 = 700
    # Final = 7000 - 700 + 500 = 6800
    premium = calculator.calculate_premium_alt(
        car_value=100000.0,
        rate=0.07,
        deductible_percentage=0.10,
        broker_fee=500.0
    )
    assert abs(premium - 6800.0) < 0.01

def test_calculate_policy_limit_with_deductible(calculator):
    """Testa o cálculo do limite da apólice com franquia."""
    # Regra: Final Policy Limit = Base Policy Limit - Deductible Value
    # Base Policy Limit = car value * coverage percentage (default 100%)
    # Deductible Value = base policy limit * deductible percentage
    # Exemplo: 100k, deductible 10%
    # Base Limit = 100k * 1.0 = 100k
    # Deductible Value = 100k * 0.10 = 10k
    # Final Limit = 100k - 10k = 90k
    limit = calculator.calculate_policy_limit_alt(
        car_value=100000.0,
        deductible_percentage=0.10
    )
    assert abs(limit - 90000.0) < 0.01

def test_invalid_car_info_raises_error(calculator):
    """Testa se informações inválidas do carro geram erro."""
    # Usar limites de conftest.py: MIN_CAR_YEAR=2000, MAX_CAR_VALUE=500000.0
    # MIN_DEDUCTIBLE=0.05, MAX_DEDUCTIBLE=0.15, MIN_BROKER=0.05, MAX_BROKER=0.15
    
    # Ano do carro menor que o mínimo (2000)
    with pytest.raises(InvalidCarInfoError):
        calculator.calculate_rate_alt(
            car_year=1999, 
            car_value=100000.0,
            registration_state="SP"
        )

    # Valor do carro maior que o máximo (500000.0)
    with pytest.raises(InvalidCarInfoError):
        calculator.calculate_rate_alt(
            car_year=2023,
            car_value=500001.0, 
            registration_state="SP"
        )

    # Estado de registro inválido
    with pytest.raises(InvalidCarInfoError):
        calculator.calculate_rate_alt(
            car_year=2023,
            car_value=100000.0,
            registration_state="XX" # Inválido
        )

    # Franquia menor que o mínimo (0.05)
    with pytest.raises(InvalidCarInfoError):
        calculator.calculate_premium_alt(
            car_value=100000.0,
            rate=0.14,
            deductible_percentage=0.04, # Menor que 0.05
            broker_fee=0.10 # Broker fee como porcentagem aqui
        )

    # Franquia maior que o máximo (0.15)
    with pytest.raises(InvalidCarInfoError):
        calculator.calculate_premium_alt(
            car_value=100000.0,
            rate=0.14,
            deductible_percentage=0.16, # Maior que 0.15
            broker_fee=0.10
        )

    # Taxa do corretor (como %) menor que o mínimo (0.05)
    with pytest.raises(InvalidCarInfoError):
        calculator.calculate_premium_alt(
            car_value=100000.0,
            rate=0.14,
            deductible_percentage=0.10,
            broker_fee=0.04 # Menor que 0.05
        )

    # Taxa do corretor (como %) maior que o máximo (0.15)
    with pytest.raises(InvalidCarInfoError):
        calculator.calculate_premium_alt(
            car_value=100000.0,
            rate=0.14,
            deductible_percentage=0.10,
            broker_fee=0.16 # Maior que 0.15
        ) 