"""
Configurações de logging.
"""
import logging
from pydantic import Field
from typing import Optional
from .base import BaseConfig
from fastapi import Request
from logging.handlers import RotatingFileHandler
import os
import time

class LoggingConfig(BaseConfig):
    """Configurações de logging."""
    
    LEVEL: str = Field(default="INFO", description="Nível de log")
    FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Formato do log")
    FILE: Optional[str] = Field(default=None, description="Arquivo de log")
    MAX_BYTES: int = Field(default=10485760, description="Tamanho máximo do arquivo de log")
    BACKUP_COUNT: int = Field(default=5, description="Número de backups")
    
    def validate(self) -> None:
        """Valida as configurações de logging."""
        if self.LEVEL not in logging._nameToLevel:
            raise ValueError("Nível de log inválido")
        self.MAX_BYTES = self.validate_range(self.MAX_BYTES, "MAX_BYTES", 1024, 1073741824)  # 1KB a 1GB
        self.BACKUP_COUNT = self.validate_range(self.BACKUP_COUNT, "BACKUP_COUNT", 1, 100)
        
    def setup(self) -> None:
        """Configura o logging."""
        logging.basicConfig(
            level=self.LEVEL,
            format=self.FORMAT,
            filename=self.FILE
        )
        
        if self.FILE:
            handler = RotatingFileHandler(
                self.FILE,
                maxBytes=self.MAX_BYTES,
                backupCount=self.BACKUP_COUNT
            )
            handler.setFormatter(logging.Formatter(self.FORMAT))
            logging.getLogger().addHandler(handler)

# Middleware de logging
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"Request: {request.method} {request.url.path} - Processed in {process_time:.2f}s")
    return response

def setup_logging(config: LoggingConfig) -> None:
    """Configura o logging global da aplicação."""
    config.validate()
    config.setup() 