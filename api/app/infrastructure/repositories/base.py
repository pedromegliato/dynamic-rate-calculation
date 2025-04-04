"""
Classe base para repositórios.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from contextlib import asynccontextmanager
import logging
from app.domain.interfaces.repository import RepositoryInterface
from app.domain.exceptions import RepositoryError, EntityNotFoundError

T = TypeVar("T")

logger = logging.getLogger(__name__)

class BaseRepository(RepositoryInterface[T], Generic[T], ABC):
    """Classe base para repositórios."""
    
    def __init__(self, cache_enabled: bool = True, max_retries: int = 3):
        """Inicializa o repositório."""
        self._cache_enabled = cache_enabled
        self._max_retries = max_retries
        self._cache: dict = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @asynccontextmanager
    async def transaction(self):
        """Gerenciador de contexto para transações."""
        try:
            await self._begin_transaction()
            yield
            await self._commit_transaction()
        except Exception as e:
            await self._rollback_transaction()
            raise RepositoryError(f"Erro na transação: {str(e)}")
    
    @abstractmethod
    async def _begin_transaction(self):
        """Inicia uma transação."""
        pass
    
    @abstractmethod
    async def _commit_transaction(self):
        """Comita uma transação."""
        pass
    
    @abstractmethod
    async def _rollback_transaction(self):
        """Reverte uma transação."""
        pass
    
    async def _retry_operation(self, operation, max_retries: int = 3):
        """Executa uma operação com retry."""
        for attempt in range(max_retries):
            try:
                return await operation()
            except EntityNotFoundError:
                raise
            except Exception as e:
                self.logger.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt == max_retries - 1:
                    raise RepositoryError(f"Operação falhou após {max_retries} tentativas")
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Obtém uma entidade por ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Obtém todas as entidades."""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Salva uma entidade."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Deleta uma entidade."""
        pass
    
    def _get_from_cache(self, key: str) -> Optional[T]:
        """Obtém um valor do cache."""
        if not self._cache_enabled:
            return None
        return self._cache.get(key)
    
    def _set_in_cache(self, key: str, value: T) -> None:
        """Define um valor no cache."""
        if self._cache_enabled:
            self._cache[key] = value
    
    def _clear_cache(self) -> None:
        """Limpa o cache."""
        self._cache.clear() 