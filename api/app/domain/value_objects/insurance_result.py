from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional
from ..entities.car import CarInfo

class InsuranceResult(BaseModel):
    """Objeto de valor que representa o resultado de um cálculo de seguro."""
    
    id: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)
    car: CarInfo
    applied_rate: Decimal = Field(..., gt=0)
    calculated_premium: Decimal = Field(..., gt=0)
    deductible_value: Decimal = Field(..., ge=0)
    policy_limit: Decimal = Field(..., gt=0)
    gis_adjustment: Decimal = Field(..., ge=0)
    
    @classmethod
    def create(
        cls,
        id: str,
        timestamp: str,
        car: CarInfo,
        applied_rate: Decimal,
        calculated_premium: Decimal,
        deductible_value: Decimal,
        policy_limit: Decimal,
        gis_adjustment: Decimal
    ) -> 'InsuranceResult':
        return cls(
            id=id,
            timestamp=timestamp,
            car=car,
            applied_rate=applied_rate,
            calculated_premium=calculated_premium,
            deductible_value=deductible_value,
            policy_limit=policy_limit,
            gis_adjustment=gis_adjustment
        ) 