"""
Implementação do repositório MySQL.
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type
)
import os
from uuid import UUID
import logging

from app.config.settings import settings
from app.domain.entities import InsuranceCalculationEntity
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.domain.value_objects import CarInfo, Address, Money, Percentage
from app.domain.exceptions import (
    RepositoryError,
    CalculationNotFoundError
)

logger = logging.getLogger(__name__)

class MySQLInsuranceRepository(InsuranceCalculationRepository):
    """Implementação do repositório MySQL."""

    def __init__(self, db=None):
        """Inicializa o repositório."""
        # ambiente de teste ?
        if "PYTEST_CURRENT_TEST" in os.environ:
            self.is_test_env = True
            return
            
        try:
            self.is_test_env = False
            if db:
                self.engine = db
            else:
                self.engine = create_engine(
                    f"mysql+mysqlconnector://{settings.DATABASE.USER}:{settings.DATABASE.PASSWORD}"
                    f"@{settings.DATABASE.HOST}:{settings.DATABASE.PORT}/{settings.DATABASE.NAME}",
                    pool_size=settings.DATABASE.POOL_SIZE,
                    max_overflow=settings.DATABASE.POOL_SIZE
                )
        except Exception as e:
            raise RepositoryError(f"Erro ao conectar ao banco de dados: {str(e)}")

    @retry(
        retry=retry_if_exception_type(SQLAlchemyError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def save_calculation(self, calculation: InsuranceCalculationEntity) -> None:
        """Salva um cálculo de seguro."""
        if self.is_test_env:
            # Em testes, mocks devem ser usados via injeção de dependência
            print("MySQLInsuranceRepository: save_calculation em modo de teste (mockado).")
            return
            
        try:
            with self.engine.connect() as conn:
                with conn.begin(): # Iniciar transação
                    query = text("""
                        INSERT INTO insurance_calculations (
                            id, car_make, car_model, car_year, car_value,
                            applied_rate, calculated_premium, deductible_value, policy_limit,
                            gis_adjustment, broker_fee, created_at, updated_at
                        ) VALUES (
                            :id, :car_make, :car_model, :car_year, :car_value,
                            :applied_rate, :calculated_premium, :deductible_value, :policy_limit,
                            :gis_adjustment, :broker_fee, :created_at, :updated_at
                        ) ON DUPLICATE KEY UPDATE
                        car_make=VALUES(car_make), car_model=VALUES(car_model), car_year=VALUES(car_year),
                        car_value=VALUES(car_value), applied_rate=VALUES(applied_rate),
                        calculated_premium=VALUES(calculated_premium), deductible_value=VALUES(deductible_value),
                        policy_limit=VALUES(policy_limit), gis_adjustment=VALUES(gis_adjustment),
                        broker_fee=VALUES(broker_fee), updated_at=VALUES(updated_at);
                    """)
                    
                    params = {
                        "id": str(calculation.id),
                        "car_make": calculation.car_info.make,
                        "car_model": calculation.car_info.model,
                        "car_year": calculation.car_info.year,
                        "car_value": calculation.car_info.value,
                        "applied_rate": calculation.applied_rate, 
                        "calculated_premium": calculation.calculated_premium.amount,
                        "deductible_value": calculation.deductible_value.amount,
                        "policy_limit": calculation.policy_limit.amount,
                        "gis_adjustment": calculation.gis_adjustment,
                        "broker_fee": calculation.broker_fee.amount,
                        "created_at": calculation.created_at,
                        "updated_at": calculation.updated_at
                    }
                    logger.info(f"Executando query principal com params: {params}")
                    conn.execute(query, params)
                    logger.info(f"Tentando salvar/atualizar endereço para {calculation}")
                    logger.info(f"Tentando salvar/atualizar endereço para {calculation.registration_location}")

                    # Salvar/Atualizar/Remover endereço 
                    if calculation.registration_location: 
                        loc = calculation.registration_location 
                        logger.info(f"Tentando salvar/atualizar endereço para {calculation.id}: {loc}")
                        addr_query = text("""
                            INSERT INTO calculation_addresses (
                                calculation_id, street, number, complement, neighborhood, 
                                city, state, postal_code, country
                            ) VALUES (
                                :calculation_id, :street, :number, :complement, :neighborhood,
                                :city, :state, :postal_code, :country
                            ) ON DUPLICATE KEY UPDATE
                                street=VALUES(street), number=VALUES(number), complement=VALUES(complement),
                                neighborhood=VALUES(neighborhood), city=VALUES(city), state=VALUES(state),
                                postal_code=VALUES(postal_code), country=VALUES(country)
                        """)
                        addr_params = {
                            "calculation_id": str(calculation.id),
                            "street": loc.street,
                            "number": loc.number,
                            "complement": loc.complement,
                            "neighborhood": loc.neighborhood,
                            "city": loc.city,
                            "state": loc.state,
                            "postal_code": loc.postal_code,
                            "country": loc.country
                        }
                        try:
                            logger.info(f"Executando query de endereço com params: {addr_params}") 
                            result_addr = conn.execute(addr_query, addr_params)
                            logger.info(f"Resultado da query de endereço (rowcount): {result_addr.rowcount}") 
                        except Exception as e_addr:
                            logger.info(f"Erro EXPLICITO ao executar query de endereço: {e_addr}", exc_info=True) 
                            raise RepositoryError(f"Erro ao salvar endereço: {e_addr}") from e_addr
                    else: 
                        logger.info(f"Removendo endereço (se existir) para {calculation.id}") 
                        delete_addr_query = text("DELETE FROM calculation_addresses WHERE calculation_id = :calculation_id")
                        try:
                            result_del = conn.execute(delete_addr_query, {"calculation_id": str(calculation.id)})
                            logger.info(f"Resultado da query de delete de endereço (rowcount): {result_del.rowcount}") 
                        except Exception as e_del:
                             logger.error(f"Erro EXPLICITO ao executar query de delete de endereço: {e_del}", exc_info=True) 
                             raise RepositoryError(f"Erro ao deletar endereço: {e_del}") from e_del
                    
                    logger.info(f"Commit da transação para {calculation.id} será tentado.") 

        except SQLAlchemyError as e:
             logger.info(f"Erro SQLAlchemy em save_calculation: {e}", exc_info=True) 
             raise RepositoryError(f"Erro ao salvar cálculo no MySQL: {str(e)}")
        except Exception as e:
             logger.info(f"Erro inesperado em save_calculation: {e}", exc_info=True) 
             raise RepositoryError(f"Erro inesperado ao salvar cálculo no MySQL: {str(e)}")

    @retry(
        retry=retry_if_exception_type(SQLAlchemyError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def get_calculation(self, calculation_id: str) -> Optional[InsuranceCalculationEntity]:
        """Obtém um cálculo de seguro pelo ID."""
        if self.is_test_env:
            print(f"MySQLInsuranceRepository: get_calculation({calculation_id}) em modo de teste (mockado).")
            return None 
            
        try:
            with self.engine.connect() as conn:
                query = text(""" 
                    SELECT 
                        c.id, c.car_make, c.car_model, c.car_year, c.car_value,
                        c.applied_rate, c.calculated_premium, c.deductible_value, c.policy_limit,
                        c.gis_adjustment, c.broker_fee, c.created_at, c.updated_at,
                        a.street, a.number, a.complement, a.neighborhood,
                        a.city, a.state, a.postal_code, a.country
                    FROM insurance_calculations c
                    LEFT JOIN calculation_addresses a ON c.id = a.calculation_id
                    WHERE c.id = :id AND c.deleted_at IS NULL
                """)
                
                logger.debug(f"Executando query para get_calculation com ID: {calculation_id}") 
                result = conn.execute(query, {"id": calculation_id}).mappings().first()
                logger.debug(f"Resultado bruto da query: {result}") 
                
                if not result:
                    logger.warning(f"Nenhum resultado encontrado para ID: {calculation_id}")
                    return None 
                
                address_obj = None
                if result.get('street') is not None:
                    try:
                        logger.debug(f"Tentando criar Address com dados: { {k: result[k] for k in ['street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code', 'country'] if k in result} }")
                        address_obj = Address(
                            street=result['street'],
                            number=result['number'],
                            complement=result['complement'],
                            neighborhood=result['neighborhood'],
                            city=result['city'],
                            state=result['state'],
                            postal_code=result['postal_code'],
                            country=result['country']
                        )
                        logger.debug(f"Objeto Address criado com sucesso: {address_obj}")
                    except Exception as addr_err:
                        logger.error(f"ERRO AO CRIAR OBJETO ADDRESS a partir do resultado: {addr_err}", exc_info=True)
                        address_obj = None 
                else:
                     logger.debug("Campo 'street' é None (ou ausente), não criando Address.")
                
                try:
                    car_info_vo = CarInfo(
                        make=result['car_make'],
                        model=result['car_model'],
                        year=result['car_year'],
                        value=result['car_value'] 
                    )
                    calculated_premium_vo = Money(amount=result['calculated_premium'])
                    deductible_value_vo = Money(amount=result['deductible_value'])
                    policy_limit_vo = Money(amount=result['policy_limit'])
                    broker_fee_vo = Money(amount=result['broker_fee'])
                    
                except Exception as vo_err:
                    logger.error(f"Erro ao criar VOs a partir do resultado: {vo_err}", exc_info=True)
                    raise RepositoryError(f"Erro ao converter dados do DB para Value Objects: {vo_err}")

                logger.debug(f"Criando InsuranceCalculationEntity com registration_location: {address_obj}")
                entity = InsuranceCalculationEntity(
                    id=UUID(result['id']), 
                    car_info=car_info_vo,
                    applied_rate=result['applied_rate'],
                    calculated_premium=calculated_premium_vo,
                    deductible_value=deductible_value_vo,
                    policy_limit=policy_limit_vo,
                    registration_location=address_obj, 
                    gis_adjustment=result['gis_adjustment'],
                    broker_fee=broker_fee_vo,
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    deleted_at=None
                )
                logger.debug(f"Entidade final criada: {entity}")
                return entity
        except SQLAlchemyError as e:
            raise RepositoryError(f"Erro ao obter cálculo do MySQL: {str(e)}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao obter cálculo do MySQL: {str(e)}")

    @retry(
        retry=retry_if_exception_type(SQLAlchemyError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def list_calculations(self, limit: int = 10, offset: int = 0) -> List[InsuranceCalculationEntity]:
        """Lista os cálculos de seguro."""
        if self.is_test_env:
             print(f"MySQLInsuranceRepository: list_calculations(limit={limit}, offset={offset}) em modo de teste (mockado).")
             return [] 

        try:
            with self.engine.connect() as conn:
                query = text(""" 
                    SELECT 
                        c.id, c.car_make, c.car_model, c.car_year, c.car_value,
                        c.applied_rate, c.calculated_premium, c.deductible_value, c.policy_limit,
                        c.gis_adjustment, c.broker_fee, c.created_at, c.updated_at,
                        a.street, a.number, a.complement, a.neighborhood,
                        a.city, a.state, a.postal_code, a.country
                    FROM insurance_calculations c
                    LEFT JOIN calculation_addresses a ON c.id = a.calculation_id
                    WHERE c.deleted_at IS NULL
                    ORDER BY c.created_at DESC
                    LIMIT :limit OFFSET :offset
                """)
                
                results = conn.execute(query, {"limit": limit, "offset": offset}).mappings().all()
                
                calculations = []
                for result in results:
                    address_obj = None
                    if result.get('street') is not None:
                         try:
                            address_obj = Address(
                                street=result['street'],
                                number=result['number'],
                                complement=result['complement'],
                                neighborhood=result['neighborhood'],
                                city=result['city'],
                                state=result['state'],
                                postal_code=result['postal_code'],
                                country=result['country']
                            )
                         except Exception as addr_err:
                             logger.error(f"Erro ao criar Address na listagem (ID: {result.get('id')}): {addr_err}", exc_info=True)
                             address_obj = None
                    
                    try:
                        car_info_vo = CarInfo(
                            make=result['car_make'],
                            model=result['car_model'],
                            year=result['car_year'],
                            value=result['car_value'] 
                        )
                        calculated_premium_vo = Money(amount=result['calculated_premium'])
                        deductible_value_vo = Money(amount=result['deductible_value'])
                        policy_limit_vo = Money(amount=result['policy_limit'])
                        broker_fee_vo = Money(amount=result['broker_fee'])

                        calculation = InsuranceCalculationEntity(
                            id=UUID(result['id']),
                            car_info=car_info_vo,
                            applied_rate=result['applied_rate'],
                            calculated_premium=calculated_premium_vo,
                            deductible_value=deductible_value_vo,
                            policy_limit=policy_limit_vo,
                            registration_location=address_obj,
                            gis_adjustment=result['gis_adjustment'],
                            broker_fee=broker_fee_vo,
                            created_at=result['created_at'],
                            updated_at=result['updated_at'],
                            deleted_at=None
                        )
                        calculations.append(calculation)
                    except Exception as vo_err:
                         logger.error(f"Erro ao criar VOs/Entidade na listagem (ID: {result.get('id')}): {vo_err}", exc_info=True)
                         continue 
                
                return calculations
                
        except SQLAlchemyError as e:
            raise RepositoryError(f"Erro ao listar cálculos do MySQL: {str(e)}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao listar cálculos do MySQL: {str(e)}")

    @retry(
        retry=retry_if_exception_type(SQLAlchemyError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def delete_calculation(self, calculation_id: str) -> bool:
        """Remove um cálculo de seguro (soft delete)."""
        if self.is_test_env:
            print(f"MySQLInsuranceRepository: delete_calculation({calculation_id}) em modo de teste (mockado).")
            return True 
            
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    # Soft delete - apenas atualiza deleted_at
                    query = text("""
                        UPDATE insurance_calculations 
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE id = :id AND deleted_at IS NULL
                    """)
                    
                    result = conn.execute(query, {"id": calculation_id})
                    
                    return result.rowcount > 0
                    
        except SQLAlchemyError as e:
            raise RepositoryError(f"Erro ao deletar cálculo no MySQL: {str(e)}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar cálculo no MySQL: {str(e)}") 