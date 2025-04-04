"""
Interface do serviço de seguros.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.value_objects import CarInfo, Percentage, Money, Address 
from app.domain.entities import InsuranceCalculationEntity 

class InsuranceService(ABC):
    """Interface para o serviço de domínio de cálculo de seguros."""
    
    @abstractmethod
    async def calculate_insurance(
        self,
        car_info: CarInfo, 
        deductible_percentage: Percentage, 
        broker_fee: Money, 
        registration_location: Optional[Address] = None 
    ) -> InsuranceCalculationEntity:
        """
        Calcula o seguro para um veículo.
        
        Args:
            car_info: Informações do carro (Value Object).
            deductible_percentage: Porcentagem da franquia (Value Object).
            broker_fee: Taxa do corretor (Value Object Money).
            registration_location: Localização de registro (Value Object Address, opcional).
            
        Returns:
            Entidade InsuranceCalculationEntity com os resultados do cálculo.
            
        Raises:
            InvalidCarInfoError: Se alguma informação de entrada for inválida.
            Exception: Para outros erros durante o cálculo.
        """
        pass