"""
Repositório de seguros.
"""
from typing import List, Optional
from app.domain.models.insurance import Insurance
from app.infrastructure.repositories.base import BaseRepository
from app.domain.exceptions import EntityNotFoundError

class InsuranceEntityRepository(BaseRepository[Insurance]):
    """Repositório de entidades de seguro."""
    
    async def get_by_id(self, id: str) -> Optional[Insurance]:
        """Obtém um seguro pelo ID."""
        try:
            # Tenta obter do cache primeiro
            cached = self._get_from_cache(f"insurance_{id}")
            if cached:
                return cached
                
            # Se não estiver no cache, busca do banco
            insurance = await self._retry_operation(self._get_by_id_impl, id)
            if insurance:
                self._set_in_cache(f"insurance_{id}", insurance)
            return insurance
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise EntityNotFoundError(f"Erro ao buscar seguro {id}: {str(e)}")
    
    async def get_all(self) -> List[Insurance]:
        """Obtém todos os seguros."""
        try:
            return await self._retry_operation(self._get_all_impl)
        except Exception as e:
            raise EntityNotFoundError(f"Erro ao buscar seguros: {str(e)}")
    
    async def save(self, insurance: Insurance) -> Insurance:
        """Salva um seguro."""
        try:
            async with self.transaction():
                saved = await self._retry_operation(self._save_impl, insurance)
                self._set_in_cache(f"insurance_{saved.id}", saved)
                return saved
        except Exception as e:
            raise EntityNotFoundError(f"Erro ao salvar seguro: {str(e)}")
    
    async def delete(self, id: str) -> bool:
        """Deleta um seguro."""
        try:
            async with self.transaction():
                deleted = await self._retry_operation(self._delete_impl, id)
                if deleted:
                    self._clear_cache()
                return deleted
        except Exception as e:
            raise EntityNotFoundError(f"Erro ao deletar seguro {id}: {str(e)}")
    
    async def _get_by_id_impl(self, id: str) -> Optional[Insurance]:
        """Implementação específica para obter um seguro pelo ID."""
        pass
    
    async def _get_all_impl(self) -> List[Insurance]:
        """Implementação específica para obter todos os seguros."""
        pass
    
    async def _save_impl(self, insurance: Insurance) -> Insurance:
        """Implementação específica para salvar um seguro."""
        pass
    
    async def _delete_impl(self, id: str) -> bool:
        """Implementação específica para deletar um seguro."""
        pass 