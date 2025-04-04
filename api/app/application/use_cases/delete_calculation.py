"""Caso de uso para deletar (soft delete) um cálculo de seguro."""

import logging
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.domain.exceptions import RepositoryError, CalculationNotFoundError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.config.settings import settings

logger = logging.getLogger(__name__)

class DeleteCalculationUseCase:
    """Caso de uso para marcar um cálculo como deletado."""

    def __init__(self, repository: InsuranceCalculationRepository):
        """
        Inicializa o caso de uso.
        Args:
            repository: Repositório para interagir com os dados.
        """
        self.repository = repository

    @retry(
        retry=retry_if_exception_type(RepositoryError),
        stop=stop_after_attempt(settings.RETRY.MAX_RETRIES),
        wait=wait_fixed(settings.RETRY.RETRY_DELAY),
        reraise=True
    )
    async def execute(self, calculation_id: str) -> bool:
        """
        Executa o soft delete.

        Args:
            calculation_id: O ID do cálculo a ser deletado.

        Returns:
            True se o cálculo foi encontrado e marcado como deletado,
            False se o cálculo não foi encontrado (ou já estava deletado).

        Raises:
            RepositoryError: Se ocorrer um erro de comunicação com o repositório.
        """
        try:
            logger.info(f"Tentando marcar cálculo ID {calculation_id} como deletado.")
            success = await self.repository.delete_calculation(calculation_id)
            if success:
                logger.info(f"Cálculo ID {calculation_id} marcado como deletado com sucesso.")
            else:
                logger.warning(f"Cálculo ID {calculation_id} não encontrado ou já deletado.")
            return success
        except RepositoryError as e:
            logger.error(f"Erro de repositório ao deletar cálculo {calculation_id}: {e}", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao deletar cálculo {calculation_id}: {e}", exc_info=True)
            raise RepositoryError(f"Erro inesperado ao deletar cálculo {calculation_id}: {str(e)}") 