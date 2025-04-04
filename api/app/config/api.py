"""
Configurações da API.
"""
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict
from typing import List
from .base import BaseConfig

class APIConfig(BaseConfig):
    """Configurações da API."""
    
    TITLE: str = Field(default="Insurance Calculation API", description="Título da API")
    DESCRIPTION: str = Field(default="API para cálculo de seguro automotivo.", description="Descrição da API")
    VERSION: str = Field(default="1.0.0", description="Versão da API")
    
    HOST: str = Field(default="0.0.0.0", description="Host da API")
    PORT: int = Field(default=8000, description="Porta da API")
    WORKERS: int = Field(default=4, description="Número de workers")
    PREFIX: str = Field(default="/api/v1", description="Prefixo da API")
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"], description="Origens permitidas pelo CORS")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Limite de requisições por período")
    RATE_LIMIT_MINUTES: int = Field(default=1, description="Período do limite de requisições em minutos")
    COMPRESSION_MIN_SIZE: int = Field(default=1000, description="Tamanho mínimo em bytes para compressão gzip")
    
    @field_validator("PORT")
    def validate_port_number(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Porta deve estar entre 1 e 65535")
        return v

    @field_validator("WORKERS", "RATE_LIMIT_REQUESTS", "RATE_LIMIT_MINUTES", "COMPRESSION_MIN_SIZE")
    def validate_positive_gt_zero(cls, v: int, info) -> int:
        if v <= 0:
            raise ValueError(f"{info.field_name} deve ser positivo")
        return v

    @field_validator("PREFIX")
    def validate_prefix_format(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("Prefixo da API deve começar com /")
        if " " in v:
             raise ValueError("Prefixo da API não pode conter espaços")
        return v

    model_config = SettingsConfigDict(env_prefix='API_', env_file='.env', env_file_encoding='utf-8', extra='ignore')