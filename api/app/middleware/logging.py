"""
Middleware de logging.
"""
import time
import logging
from fastapi import Request
from typing import Callable
from app.config.settings import settings

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next: Callable):
    """
    Middleware para logging de requisições.
    
    Args:
        request: Requisição
        call_next: Próxima função na cadeia de middlewares
        
    Returns:
        Response da requisição
    """
    start_time = time.time()
    
    # Log da requisição
    logger.info(
        f"Iniciando requisição {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_host": request.client.host if request.client else None,
            "query_params": str(request.query_params),
        }
    )
    
    try:
        # Executa a requisição
        response = await call_next(request)
        
        # Calcula o tempo de processamento
        process_time = time.time() - start_time
        
        # Log da resposta
        logger.info(
            f"Finalizando requisição {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.2f}s"
            }
        )
        
        # Adiciona headers de tempo de processamento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log de erro
        logger.error(
            f"Erro na requisição {request.method} {request.url.path}: {str(e)}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error": str(e)
            },
            exc_info=True
        )
        raise 