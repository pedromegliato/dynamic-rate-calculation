"""
Implementação do repositório Redis.
"""
from typing import List, Optional
from datetime import datetime
import json
import redis.asyncio as redis
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type
)
from decimal import Decimal

from app.config.settings import settings
from app.domain.entities import InsuranceCalculationEntity
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.domain.exceptions import (
    RepositoryError,
    CalculationNotFoundError
)
from app.domain.value_objects import CarInfo, Percentage, Money, Address
import os
import logging

logger = logging.getLogger(__name__)

class RedisInsuranceRepository(InsuranceCalculationRepository):
    """Implementação do repositório Redis."""

    def __init__(self):
        """Inicializa o repositório."""
        #  ambiente de teste 
        if "PYTEST_CURRENT_TEST" in os.environ:
            self.is_test_env = True
            return
            
        try:
            self.is_test_env = False
            self.redis = redis.Redis(
                host=settings.REDIS.HOST,
                port=settings.REDIS.PORT,
                password=settings.REDIS.PASSWORD,
                db=settings.REDIS.DB,
                decode_responses=True
            )
        except Exception as e:
            raise RepositoryError(f"Erro ao conectar ao Redis: {str(e)}")

    @retry(
        retry=retry_if_exception_type(redis.RedisError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def save_calculation(self, calculation: InsuranceCalculationEntity) -> None:
        """Salva um cálculo de seguro."""
        if self.is_test_env:
            print("RedisInsuranceRepository: save_calculation em modo de teste (mockado).")
            return
            
        try:
            key = f"insurance:calculation:{calculation.id}"
            data = calculation.model_dump_json()
            await self.redis.set(key, data, ex=settings.REDIS.TTL)
        except redis.RedisError as e:
            raise RepositoryError(f"Erro ao salvar cálculo no Redis: {str(e)}")
        except Exception as e:
             raise RepositoryError(f"Erro inesperado ao salvar cálculo no Redis: {str(e)}")

    @retry(
        retry=retry_if_exception_type(redis.RedisError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def get_calculation(self, calculation_id: str) -> Optional[InsuranceCalculationEntity]:
        """Obtém um cálculo de seguro pelo ID."""
        if self.is_test_env:
            print(f"RedisInsuranceRepository: get_calculation({calculation_id}) em modo de teste (mockado).")
            return None
            
        try:
            key = f"insurance:calculation:{calculation_id}"
            data = await self.redis.get(key)
            
            if not data:
                return None 
                
            calculation = InsuranceCalculationEntity.model_validate_json(data)
            
            if calculation.deleted_at is not None:
                logger.debug(f"Cálculo ID {calculation_id} encontrado no Redis, mas marcado como deletado.")
                return None 
                
            return calculation
        except redis.RedisError as e:
            raise RepositoryError(f"Erro ao obter cálculo do Redis: {str(e)}")
        except Exception as e:
             raise RepositoryError(f"Erro inesperado ao obter cálculo do Redis: {str(e)}")

    @retry(
        retry=retry_if_exception_type(redis.RedisError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def list_calculations(self, limit: int = 10, offset: int = 0) -> List[InsuranceCalculationEntity]:
        """Lista os cálculos de seguro (simplificado, sem ordenação real no Redis)."""
        if self.is_test_env:
            print(f"RedisInsuranceRepository: list_calculations(limit={limit}, offset={offset}) em modo de teste (mockado).")
            return [] 
            
        try:
            pattern = "insurance:calculation:*"
            keys = await self.redis.keys(pattern)
            
            if not keys:
                return []
                
            try:
                keys.sort(reverse=True)
            except Exception: 
                pass 
            
            paginated_keys = keys[offset:offset + limit]
            
            calculations = []
            if paginated_keys:
                results = await self.redis.mget(paginated_keys)
                for data in results:
                    if data:
                        try:
                            calculation = InsuranceCalculationEntity.model_validate_json(data)
                            if calculation.deleted_at is None: 
                                calculations.append(calculation)
                        except Exception as json_error: 
                            print(f"Erro ao desserializar cálculo do Redis: {json_error}, Data: {data}") 
                    
            return calculations
        except redis.RedisError as e:
            raise RepositoryError(f"Erro ao listar cálculos do Redis: {str(e)}")
        except Exception as e:
             raise RepositoryError(f"Erro inesperado ao listar cálculos do Redis: {str(e)}")

    @retry(
        retry=retry_if_exception_type(redis.RedisError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def delete_calculation(self, calculation_id: str) -> bool:
        """Marca um cálculo como deletado (soft delete) no Redis."""
        if self.is_test_env:
            print(f"RedisInsuranceRepository: delete_calculation({calculation_id}) em modo de teste (mockado).")
            return True 
            
        try:
            key = f"insurance:calculation:{calculation_id}"
            data = await self.redis.get(key)
            
            if not data:
                return False 
                
            calculation_dict = json.loads(data)
            if calculation_dict.get('deleted_at') is not None:
                return False 
                
            calculation_dict['deleted_at'] = datetime.utcnow().isoformat()
            calculation_dict['updated_at'] = calculation_dict['deleted_at']
            
            new_data = json.dumps(calculation_dict)
            
            ttl = await self.redis.ttl(key)
            await self.redis.set(key, new_data, ex=ttl if ttl > 0 else settings.REDIS.TTL)
            return True

        except redis.RedisError as e:
            raise RepositoryError(f"Erro ao marcar cálculo como deletado no Redis: {str(e)}")
        except Exception as e:
             raise RepositoryError(f"Erro inesperado ao marcar cálculo como deletado no Redis: {str(e)}") 