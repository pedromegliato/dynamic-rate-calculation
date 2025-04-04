import logging
from decimal import Decimal
from typing import Optional, Dict, Any
import dataclasses

from app.domain.entities import InsuranceCalculationEntity
from app.domain.interfaces import InsuranceCalculationRepository, InsuranceConfig as InsuranceConfigInterface
from app.domain.exceptions import CalculationNotFoundError, RepositoryError, InvalidCarInfoError
from app.domain.services import InsuranceCalculator
from app.domain.value_objects import CarInfo, Money, Percentage, Address as DomainAddress
from app.application.dtos.insurance import InsuranceCalculationPatchRequest, AddressRequest
from app.config.settings import Settings

logger = logging.getLogger(__name__)

class UpdateInsuranceCalculationUseCase:
    """Caso de uso para atualizar parcialmente um cálculo de seguro existente."""

    def __init__(self, repository: InsuranceCalculationRepository, app_settings: Settings):
        self.repository = repository
        self.app_settings = app_settings
        self.calculator = InsuranceCalculator(self.app_settings)

    async def execute(self, calculation_id: str, patch_data: InsuranceCalculationPatchRequest) -> InsuranceCalculationEntity:
        """Executa a atualização do cálculo."""
        try:
            logger.info(f"Buscando cálculo ID {calculation_id} para atualização.")
            existing_calculation = await self.repository.get_calculation(calculation_id)
            if not existing_calculation:
                logger.warning(f"Cálculo ID {calculation_id} não encontrado para atualização.")
                raise CalculationNotFoundError(f"Cálculo com ID {calculation_id} não encontrado")

            update_payload = patch_data.model_dump(exclude_unset=True)
            needs_recalculation = False
            
            updated_car_info_data = dataclasses.asdict(existing_calculation.car_info)
            
            updated_address_data: Optional[Dict[str, Any]] = None
            if existing_calculation.registration_location:
                 updated_address_data = existing_calculation.registration_location.model_dump()

            if 'make' in update_payload: updated_car_info_data['make'] = update_payload['make']; needs_recalculation = True
            if 'model' in update_payload: updated_car_info_data['model'] = update_payload['model']; needs_recalculation = True
            if 'year' in update_payload: updated_car_info_data['year'] = update_payload['year']; needs_recalculation = True
            if 'value' in update_payload: 
                updated_car_info_data['value'] = Decimal(str(update_payload['value']))
                needs_recalculation = True
            else:
                updated_car_info_data['value'] = existing_calculation.car_info.value.amount
            
            if 'registration_location' in update_payload:
                needs_recalculation = True 
                if update_payload['registration_location'] is None:
                    updated_address_data = None
                else:
                    address_dto = AddressRequest(**update_payload['registration_location'])
                    updated_address_data = address_dto.model_dump()
            
            try:
                updated_car_info = CarInfo(
                    make=updated_car_info_data['make'],
                    model=updated_car_info_data['model'],
                    year=updated_car_info_data['year'],
                    value=updated_car_info_data['value']
                )
            except ValueError as e:
                 logger.error(f"Erro de validação ao atualizar CarInfo para cálculo {calculation_id}: {e}")
                 raise InvalidCarInfoError(str(e))
                 
            updated_address: Optional[DomainAddress] = None
            if updated_address_data:
                try:
                    updated_address = DomainAddress(**updated_address_data)
                except ValueError as e:
                    logger.error(f"Erro de validação ao atualizar Address para cálculo {calculation_id}: {e}")
                    raise InvalidCarInfoError(f"Dados de endereço inválidos: {e}")

            if needs_recalculation:
                logger.info(f"Recalculando seguro para ID {calculation_id} devido a alterações.")
                
                if 'deductible_percentage' not in update_payload:
                    raise InvalidCarInfoError("O campo 'deductible_percentage' é obrigatório ao atualizar campos que exigem recálculo.")
                
                current_deductible_pct_decimal = Decimal(str(update_payload['deductible_percentage']))
                current_broker_fee_decimal = Decimal(str(update_payload.get('broker_fee', existing_calculation.broker_fee.amount)))
                
                rate_vo: Percentage = self.calculator.calculate_rate(updated_car_info, updated_address) 
                
                premium_vo: Money = self.calculator.calculate_premium(
                    car_value=Money(amount=updated_car_info.value),
                    rate=rate_vo,
                    deductible_percentage=Percentage(amount=current_deductible_pct_decimal),
                    broker_fee=Money(amount=current_broker_fee_decimal)
                )
                
                policy_limit_vo: Money = self.calculator.calculate_policy_limit(
                    car_value=Money(amount=updated_car_info.value),
                    deductible_percentage=Percentage(amount=current_deductible_pct_decimal)
                )
                
                coverage_percentage = getattr(self.app_settings, 'COVERAGE_PERCENTAGE', Decimal('1.0'))
                base_policy_limit = updated_car_info.value * coverage_percentage 
                deductible_value_decimal = base_policy_limit * current_deductible_pct_decimal
                deductible_value_vo = Money(amount=deductible_value_decimal)
                
                gis_adjustment = self.calculator._calculate_gis_adjustment(updated_address) if updated_address else None

                existing_calculation.applied_rate = rate_vo.amount 
                existing_calculation.calculated_premium = premium_vo 
                existing_calculation.policy_limit = policy_limit_vo
                existing_calculation.deductible_value = deductible_value_vo
                existing_calculation.gis_adjustment = gis_adjustment
                existing_calculation.broker_fee = Money(amount=current_broker_fee_decimal) 

            else: 
                 if 'broker_fee' in update_payload:
                    existing_calculation.broker_fee = Money(amount=Decimal(str(update_payload['broker_fee'])))
                 
            existing_calculation.car_info = updated_car_info 
            existing_calculation.registration_location = updated_address 
            existing_calculation.touch()

            logger.info(f"Salvando alterações para cálculo ID {calculation_id}")
            await self.repository.save_calculation(existing_calculation) 
            logger.info(f"Cálculo ID {calculation_id} atualizado com sucesso.")
            return existing_calculation

        except CalculationNotFoundError:
            raise
        except InvalidCarInfoError as e:
             raise 
        except RepositoryError as e:
            logger.error(f"Erro de repositório ao atualizar cálculo {calculation_id}: {e}", exc_info=True)
            raise 
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar cálculo {calculation_id}: {e}", exc_info=True)
            raise RepositoryError(f"Erro inesperado ao atualizar cálculo: {e}") from e 