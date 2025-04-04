"""
Módulo de repositórios.
"""
from .mysql_repository import MySQLInsuranceRepository
from .redis_repository import RedisInsuranceRepository

__all__ = [
    'MySQLInsuranceRepository',
    'RedisInsuranceRepository',
] 