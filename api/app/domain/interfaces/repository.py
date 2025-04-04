"""
Interfaces de repositório.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from app.domain.entities import InsuranceCalculationEntity

T = TypeVar('T')

class RepositoryInterface(Generic[T], ABC):
    """
    Interface genérica para repositórios.
    """
    
    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """
        Obtém um registro pelo ID.
        
        Args:
            id: ID do registro
            
        Returns:
            Registro ou None se não encontrado
        """
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> str:
        """
        Salva um registro.
        
        Args:
            entity: Entidade a ser salva
            
        Returns:
            ID do registro salvo
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        Remove um registro.
        
        Args:
            id: ID do registro
            
        Returns:
            True se removido, False caso contrário
        """
        pass
    
    @abstractmethod
    async def list(self, limit: int = 100) -> List[T]:
        """
        Lista os registros.
        
        Args:
            limit: Limite de resultados
            
        Returns:
            Lista de registros
        """
        pass

class InsuranceCalculationRepository(ABC):
    """
    Interface específica para repositório de cálculos de seguro.
    Define métodos assíncronos para interações de I/O.
    """
    
    @abstractmethod
    async def save_calculation(self, calculation: InsuranceCalculationEntity) -> None:
        """
        Salva um cálculo de seguro.
        
        Args:
            calculation: Entidade do cálculo a ser salva.
        
        Raises:
            RepositoryError: Se ocorrer um erro durante a persistência.
        """
        pass
    
    @abstractmethod
    async def get_calculation(self, calculation_id: str) -> Optional[InsuranceCalculationEntity]:
        """
        Obtém um cálculo de seguro pelo ID.
        
        Args:
            calculation_id: ID do cálculo.
            
        Returns:
            A entidade do cálculo encontrado ou None se não existir.
            
        Raises:
            RepositoryError: Se ocorrer um erro durante a busca.
        """
        pass
    
    @abstractmethod
    async def list_calculations(self, limit: int = 10, offset: int = 0) -> List[InsuranceCalculationEntity]:
        """
        Lista os cálculos de seguro com paginação.
        
        Args:
            limit: Limite de resultados.
            offset: Deslocamento para paginação.
            
        Returns:
            Lista de entidades de cálculo.
            
        Raises:
            RepositoryError: Se ocorrer um erro durante a listagem.
        """
        pass

    @abstractmethod
    async def delete_calculation(self, calculation_id: str) -> bool:
        """
        Marca um cálculo como deletado (soft delete).
        
        Args:
            calculation_id: ID do cálculo a ser marcado como deletado.
            
        Returns:
            True se o cálculo foi encontrado e marcado, False caso contrário.
            
        Raises:
            RepositoryError: Se ocorrer um erro durante a operação.
        """
        pass 