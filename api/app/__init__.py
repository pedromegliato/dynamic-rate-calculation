"""
Módulo principal da aplicação.
"""
from .domain import (
    InsuranceConfig,
    InsuranceCalculationRepository,
    InsuranceServiceInterface
)

from .infrastructure.repositories import (
    RedisInsuranceRepository,
    MySQLInsuranceRepository
)

__all__ = [
    'InsuranceConfig',
    'InsuranceCalculationRepository',
    'InsuranceServiceInterface',
    'RedisInsuranceRepository',
    'MySQLInsuranceRepository'
] 