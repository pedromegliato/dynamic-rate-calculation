"""
Exceções do domínio.
"""
class DomainException(Exception):
    """Exceção base do domínio."""
    pass

class EntityNotFoundError(DomainException):
    """Exceção para entidade não encontrada."""
    pass

class CalculationNotFoundError(DomainException):
    """Exceção para cálculo não encontrado."""
    pass

class InvalidCarInfoError(DomainException):
    """Exceção para informações inválidas do carro."""
    pass

class InvalidRateError(DomainException):
    """Exceção para taxa inválida."""
    pass

class InvalidPremiumError(DomainException):
    """Exceção para prêmio inválido."""
    pass

class InvalidDeductibleError(DomainException):
    """Exceção para franquia inválida."""
    pass

class InvalidPolicyLimitError(DomainException):
    """Exceção para limite de apólice inválido."""
    pass

class RepositoryError(DomainException):
    """Exceção para erros de repositório."""
    pass

class InsuranceCalculationError(DomainException):
    """Exceção para erros no cálculo do seguro."""
    pass 