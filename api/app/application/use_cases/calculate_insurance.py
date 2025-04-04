"""
Caso de uso para cálculo de seguro.
"""
from decimal import Decimal
from datetime import datetime
import logging
import uuid 
from typing import Optional

from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.domain.services.insurance_calculator import InsuranceCalculator
from app.domain.entities.insurance_calculation import InsuranceCalculationEntity
from app.domain.value_objects import CarInfo, Money, Address, Percentage
from app.domain.exceptions import (
    InvalidCarInfoError,
    RepositoryError,
    InsuranceCalculationError
)
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.config.settings import settings, Settings

logger = logging.getLogger(__name__)

class CalculateInsuranceUseCase:
    """Caso de uso para cálculo de seguro."""
    
    def __init__(
        self,
        repository: InsuranceCalculationRepository,
        app_settings: Settings 
    ):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório para persistir o cálculo.
            app_settings: Configurações da aplicação.
        """
        self.calculator = InsuranceCalculator(app_settings)
        self.repository = repository
        logger.info("CalculateInsuranceUseCase inicializado.")

    @retry(
        retry=retry_if_exception_type(RepositoryError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def execute(self, **kwargs) -> InsuranceCalculationEntity:
        """
        Executa o caso de uso: valida entrada, calcula seguro e persiste.
        
        Args:
            **kwargs: Argumentos da requisição (make, model, year, value, etc.)
            
        Returns:
            Entidade do cálculo de seguro realizado e salvo.
        """
        try:
            logger.info(f"Executando caso de uso CalculateInsurance com dados: {kwargs}")
            registration_location_data = kwargs.get('registration_location')
            registration_location: Optional[Address] = None
            if isinstance(registration_location_data, dict):
                try:
                    registration_location = Address(**registration_location_data)
                    logger.info(f"Address VO criado: {registration_location}")
                except Exception as addr_err:
                    logger.error(f"Erro ao criar Address VO a partir dos dados: {addr_err}", exc_info=True)
                    raise InvalidCarInfoError(f"Dados de endereço inválidos: {addr_err}")
            elif registration_location_data is not None:
                 logger.warning(f"Tipo inesperado para registration_location: {type(registration_location_data)}")
                 pass 

            try:
                car_info = CarInfo(
                    make=kwargs['make'],
                    model=kwargs['model'],
                    year=kwargs['year'],
                    value=Decimal(str(kwargs['value']))
                )
            except Exception as car_err:
                logger.error(f"Erro ao criar CarInfo: {car_err}", exc_info=True)
                raise InvalidCarInfoError(f"Dados do carro inválidos: {car_err}")

            deductible_percentage = Percentage(amount=Decimal(str(kwargs['deductible_percentage'])))
            broker_fee = Money(amount=Decimal(str(kwargs['broker_fee'])))
            
            rate: Percentage = self.calculator.calculate_rate(
                car_info=car_info,
                registration_location=registration_location
            )
            premium: Money = self.calculator.calculate_premium(
                car_value=Money(amount=car_info.value),
                rate=rate,
                deductible_percentage=deductible_percentage,
                broker_fee=broker_fee
            )
            limit: Money = self.calculator.calculate_policy_limit(
                car_value=Money(amount=car_info.value),
                deductible_percentage=deductible_percentage
            )
            deductible_value = Money(
                amount=limit.amount * deductible_percentage.amount,
                currency=limit.currency
            )
            
            gis_adjustment_applied = None
            if registration_location:
                 try:
                    base_rate_no_gis = self.calculator.calculate_rate(car_info, None)
                    gis_adjustment_applied = rate.amount - base_rate_no_gis.amount
                 except Exception as gis_err:
                     logger.error(f"Erro ao calcular ajuste GIS: {gis_err}", exc_info=True)
                     gis_adjustment_applied = None

            calculation_entity = InsuranceCalculationEntity(
                id=uuid.uuid4(), 
                car_info=car_info,
                applied_rate=rate.amount, 
                calculated_premium=premium,
                deductible_value=deductible_value,
                policy_limit=limit,
                registration_location=registration_location,
                gis_adjustment=Decimal(str(gis_adjustment_applied)) if gis_adjustment_applied is not None else None,
                broker_fee=broker_fee,

            )

            await self.repository.save_calculation(calculation_entity)
            logger.info(f"Cálculo ID {calculation_entity.id} persistido com sucesso.")
            
            return calculation_entity
            
        except InvalidCarInfoError as e:
             logger.warning(f"Dados inválidos fornecidos para cálculo: {e}")
             raise e 
        except RepositoryError as e:
            logger.error(f"Falha ao persistir cálculo: {e}", exc_info=True)
            raise e 
        except KeyError as e:
             logger.warning(f"Argumento faltando na requisição: {e}")
             raise InvalidCarInfoError(f"Argumento obrigatório faltando: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao executar CalculateInsuranceUseCase: {e}", exc_info=True)
            raise InsuranceCalculationError(f"Erro interno ao processar o cálculo: {e}") 