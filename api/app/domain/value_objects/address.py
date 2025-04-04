"""
Value Object para representar endereços.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class Address(BaseModel):
    """
    Value Object para representar endereços.
    
    Attributes:
        street: Nome da rua
        number: Número
        complement: Complemento (opcional)
        neighborhood: Bairro
        city: Cidade
        state: Estado
        country: País (padrão: Brasil)
        postal_code: CEP
    """
    street: str = Field(..., min_length=1, max_length=100, description="Nome da rua")
    number: str = Field(..., min_length=1, max_length=10, description="Número")
    complement: Optional[str] = Field(None, min_length=1, max_length=50, description="Complemento")
    neighborhood: str = Field(..., min_length=1, max_length=50, description="Bairro")
    city: str = Field(..., min_length=1, max_length=50, description="Cidade")
    state: str = Field(..., min_length=2, max_length=2, description="Estado")
    country: str = Field(default="Brasil", min_length=1, max_length=50, description="País")
    postal_code: str = Field(..., min_length=8, max_length=9, description="CEP")
    
    @field_validator("state")
    def validate_state(cls, v: str) -> str:
        """Valida o estado."""
        if len(v) != 2:
            raise ValueError("Estado deve ter 2 caracteres")
        return v.upper()
    
    @field_validator("postal_code")
    def validate_postal_code(cls, v: str) -> str:
        """Valida o CEP."""
        v = v.replace("-", "")
        if not v.isdigit() or len(v) != 8:
            raise ValueError("CEP deve ter 8 dígitos")
        return v
    
    def __str__(self) -> str:
        """
        Retorna a representação em string do endereço.
        
        Returns:
            String formatada
        """
        parts = [
            f"{self.street}, {self.number}",
            self.complement if self.complement else None,
            self.neighborhood,
            f"{self.city} - {self.state}",
            self.country,
            self.postal_code
        ]
        return ", ".join(filter(None, parts))
    
    def __repr__(self) -> str:
        """
        Retorna a representação do endereço.
        
        Returns:
            String de representação
        """
        return f"Address(street='{self.street}', number='{self.number}', complement='{self.complement}', neighborhood='{self.neighborhood}', city='{self.city}', state='{self.state}', country='{self.country}', postal_code='{self.postal_code}')"
    
    @classmethod
    def create(
        cls,
        street: str,
        number: str,
        neighborhood: str,
        city: str,
        state: str,
        postal_code: str,
        complement: Optional[str] = None,
        country: str = "Brasil"
    ) -> 'Address':
        return cls(
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code
        ) 