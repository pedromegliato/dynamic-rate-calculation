from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from ..value_objects.address import Address

class CarInfo(BaseModel):
    """Entidade que representa as informações de um carro."""
    
    make: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=2100)
    value: Decimal = Field(..., gt=0)
    deductible_percentage: Decimal = Field(..., ge=0, le=1)
    broker_fee: Decimal = Field(..., ge=0)
    registration_location: Optional[Address] = None

    @classmethod
    def create(
        cls,
        make: str,
        model: str,
        year: int,
        value: Decimal,
        deductible_percentage: Decimal,
        broker_fee: Decimal,
        registration_location: Optional[Address] = None
    ) -> 'CarInfo':
        return cls(
            make=make,
            model=model,
            year=year,
            value=value,
            deductible_percentage=deductible_percentage,
            broker_fee=broker_fee,
            registration_location=registration_location
        ) 