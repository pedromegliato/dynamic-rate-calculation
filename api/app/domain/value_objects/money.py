"""
Value Object para representar valores monetários.
"""
from decimal import Decimal
from pydantic import Field, field_validator
from .base import BaseValueObject

class Money(BaseValueObject):
    """Representa um valor monetário."""
    
    amount: Decimal = Field(..., description="Valor monetário")
    currency: str = Field(default="BRL", description="Moeda")
    
    @field_validator("amount")
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Valida o valor monetário."""
        if v < Decimal('0'):
            raise ValueError("Valor monetário não pode ser negativo")
        return v
    
    @field_validator("currency")
    def validate_currency(cls, v: str) -> str:
        """Valida a moeda."""
        if not v or len(v) != 3:
            raise ValueError("Moeda deve ter 3 caracteres")
        return v.upper()
    
    def __add__(self, other: "Money") -> "Money":
        """Soma dois valores monetários."""
        if self.currency != other.currency:
            raise ValueError("Moedas diferentes não podem ser somadas")
        return Money(amount=self.amount + other.amount, currency=self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        """Subtrai dois valores monetários."""
        if self.currency != other.currency:
            raise ValueError("Moedas diferentes não podem ser subtraídas")
        return Money(amount=self.amount - other.amount, currency=self.currency)
    
    def __mul__(self, other: Decimal) -> "Money":
        """Multiplica um valor monetário por um número."""
        return Money(amount=self.amount * other, currency=self.currency)
    
    def __truediv__(self, other: Decimal) -> "Money":
        """Divide um valor monetário por um número."""
        if other == 0:
            raise ValueError("Divisão por zero não é permitida")
        return Money(amount=self.amount / other, currency=self.currency)
    
    def __eq__(self, other: "Money") -> bool:
        """Compara dois valores monetários."""
        return self.amount == other.amount and self.currency == other.currency
    
    def __str__(self) -> str:
        """Retorna a representação em string do valor monetário."""
        return f"{self.currency} {self.amount:.2f}"
    
    def __repr__(self) -> str:
        """Retorna a representação do valor monetário."""
        return f"Money(amount={self.amount}, currency='{self.currency}')" 