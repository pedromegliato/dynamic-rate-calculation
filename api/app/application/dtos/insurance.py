"""
DTOs para seguros.
"""
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from app.domain.value_objects.address import Address
from app.domain.value_objects import Address as DomainAddress


class AddressRequest(BaseModel):
    street: str = Field(..., min_length=1)
    number: str = Field(..., min_length=1)
    complement: Optional[str] = None
    neighborhood: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=2, max_length=2)
    postal_code: str = Field(..., pattern=r'^\d{5}-?\d{3}$')
    country: str = Field(default='BR', min_length=2, max_length=2)

    @field_validator('postal_code')
    def format_postal_code(cls, v: str) -> str:
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) == 8:
            return f'{digits[:5]}-{digits[5:]}'
        return v


class AddressResponse(BaseModel):
    """DTO para representar o endereço na resposta."""
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str
    postal_code: str
    country: str

    model_config = ConfigDict(from_attributes=True) # Permite criar a partir do VO Address


class InsuranceCalculationRequest(BaseModel):
    """DTO para requisição de cálculo de seguro na API."""
    make: str = Field(..., description="Marca do carro", min_length=1, max_length=50)
    model: str = Field(..., description="Modelo do carro", min_length=1, max_length=50)
    year: int = Field(..., description="Ano de fabricação", ge=1900)
    value: float = Field(..., description="Valor de mercado do carro", gt=0)
    deductible_percentage: float = Field(..., description="Porcentagem da franquia (0 a 1)", ge=0, le=1)
    broker_fee: float = Field(..., description="Taxa do corretor (valor monetário)", ge=0)
    registration_location: Optional[AddressRequest] = Field(None, description="Local de registro (opcional)")

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
    registration_location: Optional[AddressResponse] = None

    model_config = ConfigDict(from_attributes=True)


class InsuranceCalculationPatchRequest(BaseModel):
    make: Optional[str] = Field(None, min_length=1)
    model: Optional[str] = Field(None, min_length=1)
    year: Optional[int] = Field(None, gt=1900)
    value: Optional[Decimal] = Field(None, gt=0)
    deductible_percentage: Optional[Decimal] = Field(None, ge=0, le=1)
    broker_fee: Optional[Decimal] = Field(None, ge=0)
    registration_location: Optional[AddressRequest | None] = Field(default=None)

    @field_validator('year')
    def validate_patch_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            current_year = datetime.now().year
            if v > current_year + 1:
                raise ValueError(f'Ano não pode ser maior que {current_year + 1}')
        return v 