"""
Configurações do Redis.
"""
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict
from typing import Optional
from .base import BaseConfig


class RedisConfig(BaseConfig):
    """Configurações do Redis."""
    
    HOST: str = Field(default="redis")
    PORT: int = Field(default=6379)
    PASSWORD: Optional[str] = Field(default="secret")
    DB: int = Field(default=0)
    URL: Optional[str] = Field(default=None)
    TTL: int = Field(default=3600)
    ENABLED: bool = Field(default=True)
    PREFIX: str = Field(default="insurance:")
    MAX_CONNECTIONS: int = Field(default=10)
    SOCKET_TIMEOUT: int = Field(default=5)
    RETRY_ON_TIMEOUT: bool = Field(default=True)
    
    @field_validator("PORT")
    def validate_port_number(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Porta deve estar entre 1 e 65535")
        return v

    @field_validator("TTL")
    def validate_ttl_non_negative(cls, v: int) -> int:
         if v < 0:
             raise ValueError("TTL deve ser maior ou igual a zero")
         return v

    @field_validator("MAX_CONNECTIONS", "SOCKET_TIMEOUT")
    def validate_positive_gt_zero(cls, v: int, info) -> int:
        if v <= 0:
             raise ValueError(f"{info.field_name} deve ser positivo e maior que zero")
        return v

    model_config = SettingsConfigDict(env_prefix='REDIS_', env_file='.env', env_file_encoding='utf-8', extra='ignore') 