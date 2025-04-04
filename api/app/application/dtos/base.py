"""
Classe base para DTOs.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from decimal import Decimal
import json


class BaseDTO(BaseModel):
    """Classe base para DTOs."""
    
    def to_dict(self) -> dict:
        """
        Converte o DTO para um dicionário.
        
        Returns:
            Dicionário com os dados do DTO
        """
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BaseDTO':
        """
        Cria um DTO a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados
            
        Returns:
            DTO criado
        """
        return cls(**data)

    def model_dump(self, *args, **kwargs) -> dict:
        """Serializa o modelo para dicionário."""
        data = super().model_dump(*args, **kwargs)
        return self._serialize_decimal(data)
    
    def dict(self, *args, **kwargs) -> dict:
        """Serializa o modelo para dicionário."""
        return self.model_dump(*args, **kwargs)
    
    def _serialize_decimal(self, data: Any) -> Any:
        """Serializa valores Decimal para string."""
        if isinstance(data, Decimal):
            return str(data)
        elif isinstance(data, dict):
            return {k: self._serialize_decimal(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_decimal(item) for item in data]
        return data 