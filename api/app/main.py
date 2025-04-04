"""
Aplicação principal.
"""
import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings, Settings
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.infrastructure.repositories.mysql_repository import MySQLInsuranceRepository
from app.infrastructure.repositories.redis_repository import RedisInsuranceRepository

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Middlewares
class ResponseTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request to {request.url.path} took {process_time:.4f} seconds")
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Error processing request to {request.url.path}: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Erro interno do servidor."}
            )

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação...")
    def handle_shutdown(signum, frame):
        logger.info(f"Recebido sinal {signal.Signals(signum).name}, encerrando...")
        sys.exit(0)
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
  
    yield
    logger.info("Encerrando aplicação...")

# Aplicação FastAPI
app = FastAPI(
    title=settings.API.TITLE,
    description=settings.API.DESCRIPTION,
    version=settings.API.VERSION,
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS.split(",") if settings.ALLOWED_METHODS else ["*"],
    allow_headers=settings.ALLOWED_HEADERS.split(",") if settings.ALLOWED_HEADERS else ["*"],
)
app.add_middleware(ResponseTimeMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Injeção de Dependência
def get_settings() -> Settings:
    return settings

def get_insurance_repository() -> InsuranceCalculationRepository:
    repo_type = settings.REPOSITORY_TYPE.lower()
    if repo_type == "mysql":
        logger.info("Usando MySQLInsuranceRepository")
        return MySQLInsuranceRepository()
    elif repo_type == "redis":
        logger.info("Usando RedisInsuranceRepository")
        return RedisInsuranceRepository()
    else:
        raise ValueError(f"Tipo de repositório inválido ou não configurado: {settings.REPOSITORY_TYPE}. Use 'mysql' ou 'redis'.")

# Incluir Routers
from app.presentation.routes.insurance_routes import router as insurance_router
from app.presentation.routes.monitoring_routes import router as monitoring_router

app.include_router(insurance_router)
app.include_router(monitoring_router)

# Main Execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
        loop="uvloop",
        http="httptools",
        limit_concurrency=settings.LIMIT_CONCURRENCY,
        timeout_keep_alive=settings.TIMEOUT_KEEP_ALIVE,
        access_log=settings.ACCESS_LOG,
    )
