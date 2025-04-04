"""
Caso de uso para listar cálculos.
"""
import logging
from typing import List

from app.domain.entities import InsuranceCalculationEntity
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.domain.exceptions import RepositoryError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.config.settings import settings

logger = logging.getLogger(__name__)

class ListCalculationsUseCase:
    """Caso de uso para listar cálculos com paginação."""
    
    def __init__(self, repository: InsuranceCalculationRepository):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório para buscar os cálculos.
        """
        self.repository = repository
        
    @retry(
        retry=retry_if_exception_type(RepositoryError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def execute(self, limit: int = 10, offset: int = 0) -> List[InsuranceCalculationEntity]:
        """
        Executa o caso de uso para listar cálculos.
        
        Args:
            limit: Número máximo de resultados a retornar.
            offset: Deslocamento para iniciar a busca (paginação).
            
        Returns:
            Lista de entidades de cálculo encontradas.
            
        Raises:
            RepositoryError: Se houver erro de comunicação com o repositório.
        """
        try:
            logger.info(f"Listando cálculos com limit={limit}, offset={offset}")
            calculations = await self.repository.list_calculations(limit=limit, offset=offset)
            logger.info(f"{len(calculations)} cálculos encontrados.")
            return calculations
        except RepositoryError as e: 
            logger.error(f"Erro de repositório ao listar cálculos: {e}", exc_info=True)
            raise e 
        except Exception as e:
            logger.error(f"Erro inesperado ao listar cálculos: {e}", exc_info=True)
            raise RepositoryError(f"Erro inesperado ao listar cálculos: {str(e)}") 