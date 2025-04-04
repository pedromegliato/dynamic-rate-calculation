"""
Configurações principais da aplicação.
"""
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from decimal import Decimal
import json
import os
from pathlib import Path
from .base import BaseConfig
from .api import APIConfig
from .database import DatabaseConfig
from .logging import LoggingConfig
from .redis import RedisConfig

class RetryConfig(BaseConfig):
    """Configurações de retry."""
    
    MAX_RETRIES: int = Field(default=3, description="Número máximo de tentativas")
    RETRY_DELAY: int = Field(default=1, description="Delay entre tentativas em segundos")
    
    @field_validator("MAX_RETRIES", "RETRY_DELAY")
    def validate_positive(cls, v: int) -> int:
        """Valida se o valor é positivo."""
        if v <= 0:
            raise ValueError("Valor deve ser positivo")
        return v

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

class CircuitBreakerConfig(BaseConfig):
    """Configurações do circuit breaker."""
    
    FAILURE_THRESHOLD: int = Field(default=5, description="Limite de falhas")
    RECOVERY_TIMEOUT: int = Field(default=60, description="Tempo de recuperação em segundos")
    EXPECTED_EXCEPTION: List[str] = Field(default_factory=lambda: ["Exception"], description="Exceções esperadas")
    
    @field_validator("FAILURE_THRESHOLD", "RECOVERY_TIMEOUT")
    def validate_positive(cls, v: int) -> int:
        """Valida se o valor é positivo."""
        if v <= 0:
            raise ValueError("Valor deve ser positivo")
        return v

    model_config = SettingsConfigDict(env_prefix='CIRCUIT_BREAKER_', env_file='.env', env_file_encoding='utf-8', extra='ignore')

class InsuranceConfig(BaseConfig):
    """Configurações do seguro."""
    
    BASE_RATE: Decimal = Field(default=Decimal('0.05'), description="Taxa base do seguro")
    MIN_CAR_YEAR: int = Field(default=1900, description="Ano mínimo do carro")
    MAX_CAR_VALUE: Decimal = Field(default=Decimal('1000000'), description="Valor máximo do carro")
    MIN_DEDUCTIBLE_PERCENTAGE: Decimal = Field(default=Decimal('0.01'), description="Porcentagem mínima de franquia")
    MAX_DEDUCTIBLE_PERCENTAGE: Decimal = Field(default=Decimal('0.20'), description="Porcentagem máxima de franquia")
    MIN_BROKER_FEE: Decimal = Field(default=Decimal('0'), description="Taxa mínima do corretor")
    MAX_BROKER_FEE: Decimal = Field(default=Decimal('10000'), description="Taxa máxima do corretor")
    AGE_ADJUSTMENT_RATE: Decimal = Field(default=Decimal('0.005'), description="Taxa de ajuste por ano")
    VALUE_ADJUSTMENT_RATE: Decimal = Field(default=Decimal('0.005'), description="Taxa de ajuste por valor (a cada 10k)")
    COVERAGE_PERCENTAGE: Decimal = Field(default=Decimal('1.0'), description="Porcentagem de cobertura")
    GIS_ADJUSTMENT_RATE: Dict[str, Decimal] = Field(default_factory=dict, description="Dicionário com taxas de ajuste GIS por estado (ex: {'SP': 0.02})")
    
    @field_validator("BASE_RATE", "MIN_DEDUCTIBLE_PERCENTAGE", "MAX_DEDUCTIBLE_PERCENTAGE", "AGE_ADJUSTMENT_RATE", "VALUE_ADJUSTMENT_RATE", "COVERAGE_PERCENTAGE")
    def validate_percentage(cls, v: Decimal) -> Decimal:
        """Valida as taxas."""
        if not (Decimal(0) <= v <= Decimal(1)):
            raise ValueError("Taxa/Porcentagem deve estar entre 0 e 1")
        return v
    
    @field_validator("MIN_CAR_YEAR")
    def validate_min_year(cls, v: int) -> int:
        """Valida o ano mínimo."""
        if v < 1900:
            raise ValueError("Ano mínimo deve ser 1900 ou maior")
        return v
    
    @field_validator("MAX_CAR_VALUE", "MIN_BROKER_FEE", "MAX_BROKER_FEE")
    def validate_value(cls, v: Decimal) -> Decimal:
        """Valida os valores monetários."""
        if v < 0:
            raise ValueError("Valor não pode ser negativo")
        return v

    @field_validator("GIS_ADJUSTMENT_RATE")
    def validate_gis_rates(cls, v: Dict[str, Decimal]) -> Dict[str, Decimal]:
        for state, rate in v.items():
            if not isinstance(state, str) or len(state) != 2:
                raise ValueError(f"Chave inválida no GIS_ADJUSTMENT_RATE: '{state}'. Deve ser sigla do estado (2 letras).")
            if not isinstance(rate, Decimal):
                try:
                    v[state] = Decimal(str(rate))
                except Exception:
                    raise ValueError(f"Valor inválido para o estado '{state}' no GIS_ADJUSTMENT_RATE: '{rate}'. Deve ser Decimal.")
        return v

    model_config = SettingsConfigDict(env_prefix='INSURANCE_', env_file='.env', env_file_encoding='utf-8', extra='ignore')

class Settings(BaseSettings):
    """Configurações principais da aplicação."""
    
    # Configurações de ambiente
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    
    # Configurações de servidor (para Uvicorn)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    RELOAD: bool = Field(default=False)
    WORKERS: int = Field(default=1)
    LIMIT_CONCURRENCY: int = Field(default=100)
    TIMEOUT_KEEP_ALIVE: int = Field(default=5)
    ACCESS_LOG: bool = Field(default=True)

    # Configurações de CORS
    ALLOWED_ORIGINS: str = Field(default="*")
    ALLOWED_METHODS: str = Field(default="*")
    ALLOWED_HEADERS: str = Field(default="*")
    
    # Tipo de repositório a ser usado ('mysql', 'redis')
    REPOSITORY_TYPE: str = Field(default="mysql")
    
    # Subconfigurações
    API: APIConfig = APIConfig()
    DATABASE: DatabaseConfig = DatabaseConfig()
    LOGGING: LoggingConfig = LoggingConfig()
    REDIS: RedisConfig = RedisConfig()
    INSURANCE: InsuranceConfig = InsuranceConfig()
    RETRY: RetryConfig = RetryConfig()
    CIRCUIT_BREAKER: CircuitBreakerConfig = CircuitBreakerConfig()
    
    # configurações...
    API_COMPRESSION_MIN_SIZE: int = Field(default=1024)
    CACHE_HOST: str = Field(default="localhost")
    CACHE_PORT: int = Field(default=6379)
    CACHE_DB: int = Field(default=0)
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_DATE_FORMAT: str = Field(default="%Y-%m-%d %H:%M:%S")
    
    @field_validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Valida o ambiente."""
        valid_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Ambiente inválido. Deve ser um dos: {valid_environments}")
        return v.lower()
    
    @classmethod
    def load_from_json(cls, json_path: str) -> "Settings":
        """
        Carrega configurações de um arquivo JSON.
        
        Args:
            json_path: Caminho para o arquivo JSON
            
        Returns:
            Instância de Settings com as configurações carregadas
        """
        # Verificar se o arquivo existe
        if not os.path.exists(json_path):
            print(f"Arquivo de configuração {json_path} não encontrado. Usando configurações padrão.")
            return cls()
        
        try:
            # Carregar o arquivo JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Criar uma instância de Settings com as configurações padrão
            settings = cls()
            
            # Atualizar as configurações com os valores do JSON
            if "INSURANCE" in config_data:
                insurance_config = config_data["INSURANCE"]
                
                # Converter valores para Decimal
                for key, value in insurance_config.items():
                    if key == "GIS_ADJUSTMENT_RATE":
                        gis_rates = {}
                        for state, rate in value.items():
                            gis_rates[state] = Decimal(str(rate))
                        setattr(settings.INSURANCE, key, gis_rates)
                    else:
                        setattr(settings.INSURANCE, key, Decimal(str(value)))
            
            print(f"Configurações carregadas de {json_path}")
            return settings
            
        except Exception as e:
            print(f"Erro ao carregar configurações de {json_path}: {e}")
            return cls()

# Instância global das configurações
config_path = os.environ.get("CONFIG_PATH", "config/insurance-config.json")
settings = Settings.load_from_json(config_path)
