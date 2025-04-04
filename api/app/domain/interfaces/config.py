"""
Interface para configurações do domínio.
"""
from abc import ABC, abstractmethod
from decimal import Decimal

class InsuranceConfig(ABC):
    """Interface para configurações de seguro."""
    
    @property
    @abstractmethod
    def AGE_RATE_INCREMENT(self) -> Decimal:
        """Incremento da taxa por idade."""
        pass
    
    @property
    @abstractmethod
    def VALUE_RATE_INCREMENT(self) -> Decimal:
        """Incremento da taxa por valor."""
        pass
    
    @property
    @abstractmethod
    def VALUE_INCREMENT_BASE(self) -> Decimal:
        """Base para incremento por valor."""
        pass
    
    @property
    @abstractmethod
    def COVERAGE_PERCENTAGE(self) -> Decimal:
        """Porcentagem de cobertura."""
        pass
    
    @property
    @abstractmethod
    def GIS_MIN_VARIATION(self) -> Decimal:
        """Variação mínima do GIS."""
        pass
    
    @property
    @abstractmethod
    def GIS_MAX_VARIATION(self) -> Decimal:
        """Variação máxima do GIS."""
        pass 