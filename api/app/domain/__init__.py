"""
Módulo de domínio da aplicação.
"""
from .value_objects import (
    Money,
    Percentage,
    Address,
    CarInfo
)

from .entities import (
    InsuranceCalculationEntity
)

from .services import (
    InsuranceCalculator
)

from .interfaces import (
    InsuranceConfig,
    RepositoryInterface,
    InsuranceCalculationRepository,
    InsuranceServiceInterface
)

from .exceptions import (
    DomainException,
    EntityNotFoundError,
    CalculationNotFoundError,
    InvalidCarInfoError,
    InvalidRateError,
    InvalidPremiumError,
    InsuranceCalculationError,
    RepositoryError
)

__all__ = [
    "Money",
    "Percentage",
    "Address",
    "CarInfo",
    
    "InsuranceCalculationEntity",
    
    "InsuranceCalculator",
    
    "InsuranceServiceInterface",
    "InsuranceConfig",
    "RepositoryInterface",
    "InsuranceCalculationRepository",
    
    "DomainException",
    "EntityNotFoundError",
    "CalculationNotFoundError",
    "InvalidCarInfoError",
    "InvalidRateError",
    "InvalidPremiumError",
    "InsuranceCalculationError",
    "RepositoryError"
] 