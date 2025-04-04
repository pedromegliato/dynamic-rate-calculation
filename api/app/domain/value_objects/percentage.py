"""
Value Object para representar porcentagens.
"""
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

class Percentage(BaseModel):
    """
    Value Object para representar porcentagens.
    
    Attributes:
        amount: Valor da porcentagem (0.0 a 1.0)
    """
    amount: Decimal = Field(..., ge=0, le=1, description="Valor da porcentagem (0.0 a 1.0)")
    
    @field_validator('amount')
    def validate_amount(cls, v: Decimal) -> Decimal:
        """
        Valida o valor da porcentagem.
        
        Args:
            v: Valor a ser validado
            
        Returns:
            Valor validado
            
        Raises:
            ValueError: Se o valor estiver fora do intervalo válido
        """
        if v < 0 or v > 1:
            raise ValueError("A porcentagem deve estar entre 0 e 1")
        return v
    
    def __str__(self) -> str:
        """
        Retorna a representação em string da porcentagem.
        
        Returns:
            String formatada
        """
        return f"{float(self.amount * 100):.2f}%"
    
    def __repr__(self) -> str:
        """
        Retorna a representação da porcentagem.
        
        Returns:
            String de representação
        """
        return f"Percentage(amount={self.amount})"
    
    def __eq__(self, other: object) -> bool:
        """
        Compara duas porcentagens.
        
        Args:
            other: Outra porcentagem
            
        Returns:
            True se forem iguais, False caso contrário
        """
        if not isinstance(other, Percentage):
            return False
        return self.amount == other.amount
    
    def __lt__(self, other: object) -> bool:
        """
        Compara se uma porcentagem é menor que outra.
        
        Args:
            other: Outra porcentagem
            
        Returns:
            True se for menor, False caso contrário
            
        Raises:
            TypeError: Se o outro objeto não for uma porcentagem
        """
        if not isinstance(other, Percentage):
            raise TypeError("Comparação inválida: esperado Percentage")
        return self.amount < other.amount
    
    def __le__(self, other: object) -> bool:
        """
        Compara se uma porcentagem é menor ou igual a outra.
        
        Args:
            other: Outra porcentagem
            
        Returns:
            True se for menor ou igual, False caso contrário
            
        Raises:
            TypeError: Se o outro objeto não for uma porcentagem
        """
        if not isinstance(other, Percentage):
            raise TypeError("Comparação inválida: esperado Percentage")
        return self.amount <= other.amount
    
    def __gt__(self, other: object) -> bool:
        """
        Compara se uma porcentagem é maior que outra.
        
        Args:
            other: Outra porcentagem
            
        Returns:
            True se for maior, False caso contrário
            
        Raises:
            TypeError: Se o outro objeto não for uma porcentagem
        """
        if not isinstance(other, Percentage):
            raise TypeError("Comparação inválida: esperado Percentage")
        return self.amount > other.amount
    
    def __ge__(self, other: object) -> bool:
        """
        Compara se uma porcentagem é maior ou igual a outra.
        
        Args:
            other: Outra porcentagem
            
        Returns:
            True se for maior ou igual, False caso contrário
            
        Raises:
            TypeError: Se o outro objeto não for uma porcentagem
        """
        if not isinstance(other, Percentage):
            raise TypeError("Comparação inválida: esperado Percentage")
        return self.amount >= other.amount 