"""
Módulo de cache.
"""
import redis.asyncio as redis
from app.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


async def get_cache() -> redis.Redis:
    """
    Obtém uma conexão com o Redis.
    
    Returns:
        Conexão com o Redis
    """
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis.from_url(
                settings.REDIS.URL,
                decode_responses=True,
                socket_timeout=settings.REDIS.SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS.SOCKET_TIMEOUT,
                retry_on_timeout=settings.REDIS.RETRY_ON_TIMEOUT,
                max_connections=settings.REDIS.MAX_CONNECTIONS
            )
            await _redis_client.ping()
            logger.info("Conexão com Redis estabelecida")
        except Exception as e:
            logger.error(f"Erro ao conectar com Redis: {str(e)}")
            raise
    return _redis_client


async def close_cache() -> None:
    """
    Fecha a conexão com o Redis.
    """
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.close()
            _redis_client = None
            logger.info("Conexão com Redis fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão com Redis: {str(e)}")
            raise 