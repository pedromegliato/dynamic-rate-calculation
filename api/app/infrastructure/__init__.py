"""
Módulo de infraestrutura.
"""
from app.infrastructure.repositories import (
    MySQLInsuranceRepository,
    RedisInsuranceRepository
)
from app.infrastructure.cache import get_cache

__all__ = [
    'MySQLInsuranceRepository',
    'RedisInsuranceRepository',
    'get_cache'
] 