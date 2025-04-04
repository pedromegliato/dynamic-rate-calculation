"""
Implementação do serviço de seguro na infraestrutura.
"""
from app.domain.interfaces.service import InsuranceService as InsuranceServiceInterface
from app.domain.interfaces.config import InsuranceConfig
from app.domain.models.car import Car
from app.domain.models.insurance_result import InsuranceResult
from app.domain.exceptions import InvalidCarInfoError
from app.domain.services.insurance_calculator import InsuranceCalculator
from datetime import datetime
import uuid


class InsuranceService(InsuranceServiceInterface):
    """Implementação do serviço de seguro."""
    
    def __init__(self, config: InsuranceConfig, calculator: InsuranceCalculator):
        """
        Inicializa o serviço.
        
        Args:
            config: Configurações do seguro
            calculator: Calculador de seguro
        """
        self.config = config
        self.calculator = calculator
    
    def calculate_insurance(self, car: Car) -> InsuranceResult:
        """
        Calcula o seguro de um carro.
        
        Args:
            car: Carro para cálculo
            
        Returns:
            Resultado do cálculo
            
        Raises:
            InvalidCarInfoError: Se as informações do carro forem inválidas
        """
        try:
            # Calcular taxa base
            base_rate = self.calculator.calculate_base_rate(car)
            
            # Calcular ajuste GIS
            gis_adjustment = self.calculator.calculate_gis_adjustment(
                car.registration_location.location
            ) if car.registration_location else Percentage(0)
            
            # Calcular taxa final
            final_rate = base_rate + gis_adjustment
            
            # Calcular prêmio
            premium = self.calculator.calculate_premium(car, final_rate)
            
            # Calcular franquia
            deductible = self.calculator.calculate_deductible(car, premium)
            
            # Calcular limite da apólice
            policy_limit = self.calculator.calculate_policy_limit(car, deductible)
            
            # Criar resultado
            return InsuranceResult(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                car=car,
                applied_rate=final_rate,
                calculated_premium=premium,
                deductible_value=deductible,
                policy_limit=policy_limit,
                gis_adjustment=gis_adjustment
            )
            
        except Exception as e:
            raise InvalidCarInfoError(f"Erro ao calcular seguro: {str(e)}") 