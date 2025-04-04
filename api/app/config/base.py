"""
Configurações base da aplicação.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import os
import re

class BaseConfig(BaseModel):
    """Classe base para configurações."""
    
    ENVIRONMENT: str = Field(default="development", description="Ambiente de execução")
    
    @field_validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Valida ambiente."""
        valid_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Ambiente inválido. Deve ser um dos: {valid_environments}")
        return v.lower()
    
    @field_validator("*", mode='before')
    def validate_url_format(cls, v: Any, info: Any) -> Any:
        """Valida URLs."""
        field_name = info.field_name
        if field_name.upper().endswith("_URL") and isinstance(v, str):
            url_pattern = re.compile(
                r'^(?:http|ftp)s?://'  # http:// ..... https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ... ip
                r'(?::\d+)?'  # port
                r'(?:/?|[/?]\S+)?$', re.IGNORECASE)
                
            if not url_pattern.match(v):
                raise ValueError(f"URL inválida para {field_name}: {v}")
        return v
    
    def validate_port(self, port: int, name: str) -> int:
        """Valida uma porta."""
        if not 1 <= port <= 65535:
            raise ValueError(f"{name} deve estar entre 1 e 65535")
        return port
    
    def validate_positive(self, value: int | float, name: str) -> int | float:
        """Valida um valor positivo."""
        if value <= 0:
            raise ValueError(f"{name} deve ser positivo")
        return value
    
    def validate_non_empty(self, value: str, name: str) -> str:
        """Valida uma string não vazia."""
        if not str(value).strip():
            raise ValueError(f"{name} não pode ser vazio")
        return value
    
    def validate_range(self, value: int | float, name: str, min_value: int | float, max_value: int | float) -> int | float:
        """Valida um valor dentro de um intervalo."""
        if not min_value <= value <= max_value:
            raise ValueError(f"{name} deve estar entre {min_value} e {max_value}")
        return value
    
    def validate_path_exists(self, path: str, name: str) -> str:
        """Valida um caminho de arquivo."""
        if not os.path.exists(path):
            raise ValueError(f"{name} não existe: {path}")
        return path
    
    def validate_is_directory(self, path: str, name: str) -> str:
        """Valida um diretório."""
        validated_path = self.validate_path_exists(path, name)
        if not os.path.isdir(validated_path):
            raise ValueError(f"{name} não é um diretório: {path}")
        return validated_path
    
    model_config = ConfigDict(validate_assignment=True, extra='ignore') 