"""Rotas da API relacionadas a monitoramento e saúde."""

import logging
from typing import Dict, Any
from fastapi import APIRouter
from app.config.settings import settings 

logger = logging.getLogger(__name__)

# Router 
router = APIRouter()

# Endpoints 
@router.get("/health", tags=["health"])
async def health_check_endpoint() -> Dict[str, Any]:
    """Verifica a saúde da aplicação."""
    logger.debug("Health check solicitado.")
    api_version = getattr(getattr(settings, 'API', None), 'VERSION', 'unknown')
    return {
        "status": "ok",
        "version": api_version,
        "environment": settings.ENVIRONMENT,
    }

@router.get("/metrics", tags=["monitoring"])
async def metrics_endpoint() -> Dict[str, Any]:
    """Retorna métricas básicas da aplicação."""
    logger.debug("Métricas solicitadas.")
    try:
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }
    except ImportError:
        logger.warning("Biblioteca 'psutil' não encontrada. Métricas não disponíveis.")
        return {"error": "psutil não instalado"}
    except Exception as e:
        logger.error(f"Erro ao coletar métricas: {e}", exc_info=True)
        return {"error": "Erro ao coletar métricas"} 