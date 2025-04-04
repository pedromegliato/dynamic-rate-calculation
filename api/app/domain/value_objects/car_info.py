"""
Objeto de valor para informações do carro.
"""
from dataclasses import dataclass
from app.domain.value_objects.money import Money
from app.domain.value_objects.address import Address

@dataclass(frozen=True)
class CarInfo:
    """Informações do carro."""
    make: str
    model: str
    year: int
    value: Money
    registration_location: Address = None
    
    def __str__(self) -> str:
        """
        Retorna a representação em string das informações do carro.
        
        Returns:
            String formatada
        """
        return f"{self.make} {self.model} {self.year}"
    
    def __repr__(self) -> str:
        """
        Retorna a representação das informações do carro.
        
        Returns:
            String de representação
        """
        return f"CarInfo(make='{self.make}', model='{self.model}', year={self.year}, value={self.value})" 