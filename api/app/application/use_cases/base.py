"""
Classes base para casos de uso.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Protocol, runtime_checkable, Type, Dict, Tuple, get_type_hints, get_origin, get_args
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.application.dtos.base import BaseDTO
import inspect
import logging

@runtime_checkable
class UseCaseRequest(Protocol):
    """Protocolo para requisições de casos de uso."""
    pass

@runtime_checkable
class UseCaseResponse(Protocol):
    """Protocolo para respostas de casos de uso."""
    pass

T = TypeVar('T', bound=UseCaseRequest) 
R = TypeVar('R', bound=UseCaseResponse)  

logger = logging.getLogger(__name__)

class BaseUseCase(ABC, Generic[T, R]):
    """Classe base abstrata para casos de uso."""
    
    def __init__(self, repository: InsuranceCalculationRepository):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório de seguros
            
        Raises:
            TypeError: Se o repositório não implementar InsuranceCalculationRepository
        """
        if not isinstance(repository, InsuranceCalculationRepository):
            raise TypeError(f"repository deve implementar InsuranceCalculationRepository, recebido {type(repository)}")
        
        self._repository = repository
        
        type_hints = inspect.get_type_hints(self.__class__)
        if type_hints['_repository'] != InsuranceCalculationRepository:
            raise TypeError(f"O atributo '_repository' deve ser do tipo InsuranceCalculationRepository")
        
        self._validate_type_parameters()
        self._validate_method_signatures()
        self._validate_generic_parameters()
    
    def _validate_type_parameters(self) -> None:
        """Valida os parâmetros de tipo da classe."""
        type_args = getattr(self, "__orig_bases__", [])
        if not type_args:
            raise TypeError(f"{self.__class__.__name__} deve especificar os tipos T e R")
        if len(type_args) != 1:
            raise TypeError(f"{self.__class__.__name__} deve ter exatamente dois parâmetros de tipo")
        if not issubclass(type_args[0].__args__[0], UseCaseRequest):
            raise TypeError(f"Tipo T deve implementar UseCaseRequest")
        if not issubclass(type_args[0].__args__[1], UseCaseResponse):
            raise TypeError(f"Tipo R deve implementar UseCaseResponse")
    
    def _validate_generic_parameters(self) -> None:
        """Valida os parâmetros genéricos da classe."""
        type_hints = get_type_hints(self.__class__)
        for name, hint in type_hints.items():
            origin = get_origin(hint)
            if origin is not None:
                args = get_args(hint)
                if not all(isinstance(arg, type) for arg in args):
                    raise TypeError(f"Parâmetro genérico inválido em {name}: {hint}")
    
    def _validate_method_signatures(self) -> None:
        """Valida as assinaturas dos métodos da classe."""
        type_hints = get_type_hints(self.__class__)
        if 'execute' not in type_hints:
            raise TypeError(f"{self.__class__.__name__} deve implementar o método execute")
        if 'request' not in type_hints['execute']:
            raise TypeError(f"O método execute deve ter um parâmetro 'request'")
        if type_hints['execute']['request'] != T:
            raise TypeError(f"O parâmetro 'request' deve ser do tipo {T}")
        if type_hints['execute']['return'] != R:
            raise TypeError(f"O retorno deve ser do tipo {R}")
    
    @abstractmethod
    def execute(self, request: T, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> R:
        """
        Executa o caso de uso.
        
        Args:
            request: Requisição do caso de uso
            *args: Argumentos posicionais adicionais
            **kwargs: Argumentos nomeados adicionais
            
        Returns:
            Resposta do caso de uso
            
        Raises:
            TypeError: Se a requisição não implementar UseCaseRequest
            TypeError: Se o retorno não implementar UseCaseResponse
        """
        if not isinstance(request, UseCaseRequest):
            raise TypeError(f"request deve implementar UseCaseRequest, recebido {type(request)}")
        result = self._execute(request, *args, **kwargs)
        if not isinstance(result, UseCaseResponse):
            raise TypeError(f"O retorno deve implementar UseCaseResponse, recebido {type(result)}")
        return result
    
    @abstractmethod
    def _execute(self, request: T, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> R:
        """
        Implementação específica do caso de uso.
        
        Args:
            request: Requisição do caso de uso
            *args: Argumentos posicionais adicionais
            **kwargs: Argumentos nomeados adicionais
            
        Returns:
            Resposta do caso de uso
        """
        pass


class BaseRepositoryUseCase(BaseUseCase[T, R]):
    """Classe base para casos de uso que utilizam repositório."""
    
    def __init__(self, repository: InsuranceCalculationRepository):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório de seguros
            
        Raises:
            TypeError: Se o repositório não implementar InsuranceCalculationRepository
        """
        super().__init__(repository)
    
    def _validate_method_signatures(self) -> None:
        """Valida as assinaturas dos métodos da classe."""
        super()._validate_method_signatures()
        type_hints = get_type_hints(self.__class__)
        if '_repository' not in type_hints:
            raise TypeError(f"{self.__class__.__name__} deve ter um atributo '_repository'")
        if type_hints['_repository'] != InsuranceCalculationRepository:
            raise TypeError(f"O atributo '_repository' deve ser do tipo InsuranceCalculationRepository")


class BaseQueryUseCase(BaseRepositoryUseCase[T, R]):
    """Classe base para casos de uso de consulta."""
    
    def _execute(self, request: T, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> R:
        """
        Executa a consulta através do método _query.
        
        Args:
            request: Requisição da consulta
            *args: Argumentos posicionais adicionais
            **kwargs: Argumentos nomeados adicionais
            
        Returns:
            Resposta da consulta
            
        Raises:
            TypeError: Se a requisição não implementar UseCaseRequest
            TypeError: Se o retorno não implementar UseCaseResponse
        """
        if not isinstance(request, UseCaseRequest):
            raise TypeError(f"request deve implementar UseCaseRequest, recebido {type(request)}")
        result = self._query(request, *args, **kwargs)
        if not isinstance(result, UseCaseResponse):
            raise TypeError(f"O retorno deve implementar UseCaseResponse, recebido {type(result)}")
        return result
    
    @abstractmethod
    def _query(self, request: T, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> R:
        """
        Executa a consulta específica.
        
        Args:
            request: Requisição da consulta
            *args: Argumentos posicionais adicionais
            **kwargs: Argumentos nomeados adicionais
            
        Returns:
            Resposta da consulta
            
        Raises:
            TypeError: Se a requisição não implementar UseCaseRequest
        """
        if not isinstance(request, UseCaseRequest):
            raise TypeError(f"request deve implementar UseCaseRequest, recebido {type(request)}")
        pass 