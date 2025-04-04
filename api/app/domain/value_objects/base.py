"""
Classe base para Value Objects.
"""
from abc import ABC
from typing import Any, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from decimal import Decimal
import json

class BaseValueObject(BaseModel, ABC):
    """Classe base para Value Objects."""
    
    def __eq__(self, other: Any) -> bool:
        """Compara dois Value Objects."""
        if not isinstance(other, self.__class__):
            return False
        return self.model_dump() == other.model_dump()
    
    def __hash__(self) -> int:
        """Retorna o hash do Value Object."""
        return hash(tuple(sorted(self.model_dump().items())))
    
    def __str__(self) -> str:
        """Retorna a representação em string."""
        return str(self.model_dump())
    
    def __repr__(self) -> str:
        """Retorna a representação do objeto."""
        return f"{self.__class__.__name__}({self.model_dump()})"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseValueObject":
        """Cria um Value Object a partir de um dicionário."""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o Value Object para dicionário."""
        return self.model_dump()
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseValueObject":
        """Cria um Value Object a partir de uma string JSON."""
        return cls.from_dict(json.loads(json_str))
    
    def to_json(self) -> str:
        """Converte o Value Object para JSON."""
        return json.dumps(self.to_dict())
    
    @field_validator("*")
    def validate_required_fields(cls, v: Any, info: Any) -> Any:
        """Valida campos obrigatórios."""
        if v is None and info.field_name not in cls.model_fields:
            raise ValueError(f"Campo {info.field_name} é obrigatório")
        return v
    
    @field_validator("*")
    def validate_types(cls, v: Any, info: Any) -> Any:
        """Valida tipos específicos."""
        field_type = cls.model_fields[info.field_name].annotation
        
        if field_type == str and not isinstance(v, str):
            raise ValueError(f"Campo {info.field_name} deve ser uma string")
            
        if field_type == int and not isinstance(v, int):
            raise ValueError(f"Campo {info.field_name} deve ser um inteiro")
            
        if field_type == float and not isinstance(v, (int, float)):
            raise ValueError(f"Campo {info.field_name} deve ser um número")
            
        if field_type == Decimal and not isinstance(v, (int, float, Decimal)):
            raise ValueError(f"Campo {info.field_name} deve ser um decimal")
            
        if field_type == datetime and not isinstance(v, datetime):
            raise ValueError(f"Campo {info.field_name} deve ser uma data/hora")
            
        if field_type == date and not isinstance(v, date):
            raise ValueError(f"Campo {info.field_name} deve ser uma data")
            
        return v 