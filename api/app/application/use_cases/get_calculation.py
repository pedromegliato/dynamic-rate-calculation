"""
Caso de uso para obter um cálculo.
"""
import logging
from typing import Optional
from app.domain.entities import InsuranceCalculationEntity
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.domain.exceptions import (
    CalculationNotFoundError,
    RepositoryError
)
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GetCalculationUseCase:
    """Caso de uso para obter um cálculo pelo ID."""
    
    def __init__(self, repository: InsuranceCalculationRepository):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório para buscar o cálculo.
        """
        self.repository = repository
        
    @retry(
        retry=retry_if_exception_type(RepositoryError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def execute(self, calculation_id: str) -> InsuranceCalculationEntity:
        """
        Executa o caso de uso.
        
        Args:
            calculation_id: ID do cálculo a ser buscado.
            
        Returns:
            A entidade do cálculo encontrado.
            
        Raises:
            CalculationNotFoundError: Se o cálculo não for encontrado.
            RepositoryError: Se houver erro de comunicação com o repositório.
        """
        try:
            logger.info(f"Buscando cálculo com ID: {calculation_id}")
            calculation = await self.repository.get_calculation(calculation_id)
            if calculation is None:
                logger.warning(f"Cálculo com ID {calculation_id} não encontrado.")
                raise CalculationNotFoundError(f"Cálculo com ID {calculation_id} não encontrado.")
            
            logger.info(f"Cálculo ID {calculation_id} encontrado.")
            return calculation
            
        except CalculationNotFoundError:
            raise
        except RepositoryError as e:
             logger.error(f"Erro de repositório ao buscar cálculo {calculation_id}: {e}", exc_info=True)
             raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar cálculo {calculation_id}: {e}", exc_info=True)
            raise RepositoryError(f"Erro inesperado ao buscar cálculo {calculation_id}: {str(e)}") 