"""
Configurações do banco de dados.
"""
from pydantic import Field
from .base import BaseConfig

class DatabaseConfig(BaseConfig):
    """Configurações do banco de dados."""
    
    HOST: str = Field(default="db", description="Host do banco de dados")
    PORT: int = Field(default=3306, description="Porta do banco de dados")
    USER: str = Field(default="root", description="Usuário do banco de dados")
    PASSWORD: str = Field(default="secret", description="Senha do banco de dados")
    NAME: str = Field(default="insurance", description="Nome do banco de dados")
    POOL_SIZE: int = Field(default=5, description="Tamanho do pool de conexões")
    MAX_RETRIES: int = Field(default=3, description="Número máximo de tentativas")
    RETRY_DELAY: int = Field(default=1, description="Delay entre tentativas em segundos")
    
    def validate(self) -> None:
        """Valida as configurações do banco de dados."""
        self.PORT = self.validate_port(self.PORT)
        self.USER = self.validate_non_empty(self.USER, "USER")
        self.NAME = self.validate_non_empty(self.NAME, "NAME")
        self.POOL_SIZE = self.validate_range(self.POOL_SIZE, "POOL_SIZE", 1, 100)
        self.MAX_RETRIES = self.validate_range(self.MAX_RETRIES, "MAX_RETRIES", 1, 10)
        self.RETRY_DELAY = self.validate_range(self.RETRY_DELAY, "RETRY_DELAY", 1, 60) 