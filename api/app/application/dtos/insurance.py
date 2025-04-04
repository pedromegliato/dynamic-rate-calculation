"""
DTOs para seguros.
"""
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from app.domain.value_objects.address import Address


class InsuranceCalculationRequest(BaseModel):
    """DTO para requisição de cálculo de seguro na API."""
    make: str = Field(..., description="Marca do carro", min_length=1, max_length=50)
    model: str = Field(..., description="Modelo do carro", min_length=1, max_length=50)
    year: int = Field(..., description="Ano de fabricação", ge=1900)
    value: float = Field(..., description="Valor de mercado do carro", gt=0)
    deductible_percentage: float = Field(..., description="Porcentagem da franquia (0 a 1)", ge=0, le=1)
    broker_fee: float = Field(..., description="Taxa do corretor (valor monetário)", ge=0)
    registration_location: Optional[Address] = Field(None, description="Local de registro (opcional)")

    @field_validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Ano do carro não pode ser maior que o ano atual ({current_year})")
        return v
        
    model_config = ConfigDict(extra='ignore', from_attributes=True)


class InsuranceCalculationResponse(BaseModel):
    """DTO para resposta de cálculo de seguro."""
    id: str = Field(..., description="ID único do cálculo")
    timestamp: datetime = Field(..., description="Data e hora do cálculo")
    car_make: str = Field(..., description="Marca do carro")
    car_model: str = Field(..., description="Modelo do carro")
    car_year: int = Field(..., description="Ano do carro")
    car_value: float = Field(..., description="Valor do carro")
    applied_rate: float = Field(..., description="Taxa de seguro aplicada (final)")
    calculated_premium: float = Field(..., description="Prêmio de seguro calculado (final)")
    deductible_value: float = Field(..., description="Valor monetário da franquia")
    policy_limit: float = Field(..., description="Limite da apólice")
    gis_adjustment: Optional[float] = Field(None, description="Ajuste percentual GIS aplicado (se houver)")
    broker_fee: float = Field(..., description="Taxa do corretor aplicada")

    model_config = ConfigDict(from_attributes=True) 