"""
Entidade de cálculo de seguro.
"""
from datetime import datetime
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from app.domain.value_objects import CarInfo, Money, Percentage, Address

@dataclass
class InsuranceCalculationEntity:
    """
    Entidade que representa um cálculo de seguro.
    
    Attributes:
        car_info: Informações do carro
        applied_rate: Taxa aplicada
        calculated_premium: Prêmio calculado
        deductible_value: Valor da franquia
        policy_limit: Limite da apólice
        broker_fee: Taxa do corretor
        registration_location: Local de registro (opcional)
        gis_adjustment: Ajuste GIS (opcional)
        id: Identificador único
        created_at: Data de criação
        updated_at: Data de atualização
        deleted_at: Data de exclusão (opcional)
    """
    car_info: CarInfo
    applied_rate: Decimal
    calculated_premium: Money
    deductible_value: Money
    policy_limit: Money
    broker_fee: Money
    registration_location: Optional[Address] = None
    gis_adjustment: Optional[Decimal] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    
    def touch(self):
        """Atualiza o timestamp updated_at."""
        self.updated_at = datetime.utcnow()

    def __str__(self) -> str:
        """Retorna a representação em string do cálculo."""
        return f"InsuranceCalculation(id={self.id}, car_info={self.car_info}, applied_rate={self.applied_rate}, calculated_premium={self.calculated_premium})"
    
    def __repr__(self) -> str:
        """Retorna a representação do cálculo."""
        return f"InsuranceCalculation(id='{self.id}', car_info={self.car_info}, applied_rate={self.applied_rate}, calculated_premium={self.calculated_premium})" 