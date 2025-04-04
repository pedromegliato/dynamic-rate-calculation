"""
Gerenciamento de conexão com o banco de dados MySQL.
"""
from typing import Generator
import mysql.connector
from mysql.connector import pooling
from app.config.settings import settings
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

_db_pool = None

class MySQLConnectionPool:
    """Singleton para gerenciar o pool de conexões MySQL."""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self) -> None:
        """Inicializa o pool de conexões."""
        if self._pool is None:
            try:
                dbconfig = {
                    "host": settings.DATABASE.HOST,
                    "port": settings.DATABASE.PORT,
                    "user": settings.DATABASE.USER,
                    "password": settings.DATABASE.PASSWORD,
                    "database": settings.DATABASE.NAME,
                }
                
                self._pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=settings.DATABASE.POOL_SIZE,
                    **dbconfig
                )
                
                logger.info("Pool de conexões MySQL inicializado com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao inicializar pool de conexões MySQL: {str(e)}")
                raise
    
    def get_connection(self):
        """Obtém uma conexão do pool."""
        if self._pool is None:
            self._initialize_pool()
        return self._pool.get_connection()
    
    def close(self):
        """Fecha o pool de conexões."""
        if self._pool is not None:
            self._pool = None

@contextmanager
def get_db() -> Generator:
    """
    Gerenciador de contexto para obter uma conexão do pool.
    
    Yields:
        Conexão do pool
        
    Example:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
    """
    global _db_pool
    
    if _db_pool is None:
        _db_pool = MySQLConnectionPool()
        logger.info("Pool de conexões MySQL criado")
    
    try:
        connection = _db_pool.get_connection()
        yield connection
    except Exception as e:
        logger.error(f"Erro ao obter conexão MySQL: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

async def close_db() -> None:
    """
    Fecha o pool de conexões com o banco de dados.
    """
    global _db_pool
    if _db_pool is not None:
        try:
            _db_pool.close()
            _db_pool = None
            logger.info("Pool de conexões MySQL fechado")
        except Exception as e:
            logger.error(f"Erro ao fechar pool de conexões MySQL: {str(e)}")
            raise 