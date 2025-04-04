"""
Módulo de interfaces do domínio.
"""
from .config import InsuranceConfig
from .repository import RepositoryInterface, InsuranceCalculationRepository
from .insurance_service import InsuranceService as InsuranceServiceInterface

__all__ = [
    'InsuranceConfig',
    'RepositoryInterface',
    'InsuranceCalculationRepository',
    'InsuranceServiceInterface'
] 