"""
Implementação do serviço de seguro.
"""
from datetime import datetime
import uuid
from decimal import Decimal
from typing import Optional, List
import logging

from app.domain.interfaces.insurance_service import InsuranceService
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.domain.entities.insurance_calculation import InsuranceCalculationEntity
from app.domain.value_objects import CarInfo, Money, Percentage, Address
from app.domain.services.insurance_calculator import InsuranceCalculator
from app.config.settings import settings
from app.domain.exceptions import InvalidCarInfoError, RepositoryError, InsuranceCalculationError

logger = logging.getLogger(__name__)

class InsuranceServiceImpl(InsuranceService):
    """
    Implementação do serviço de seguro (camada de infraestrutura).
    """

    def __init__(self, settings_instance=None):
        """
        Inicializa o serviço.
        Args:
            settings_instance: Configurações (opcional).
        """
        self.settings = settings_instance or settings
        logger.debug("InsuranceServiceImpl (Infra) inicializado.")

    async def calculate_insurance(
        self,
        car_info: CarInfo,
        deductible_percentage: Percentage,
        broker_fee: Money,
        registration_location: Optional[Address] = None
    ) -> InsuranceCalculationEntity:
        """
        Método da interface. A lógica real está no InsuranceCalculator,
        que é chamado pelo CalculateInsuranceUseCase. Futuramente, talvez implementar.....
        """
        logger.warning("InsuranceServiceImpl.calculate_insurance chamado, mas a lógica principal está no UseCase/Calculator.")

        raise NotImplementedError("Use CalculateInsuranceUseCase que utiliza InsuranceCalculator diretamente.")
