"""Rotas da API relacionadas ao cálculo de seguro."""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.config.settings import settings, Settings
from app.domain.interfaces.repository import InsuranceCalculationRepository
from app.application.use_cases import (
    CalculateInsuranceUseCase,
    GetCalculationUseCase,
    ListCalculationsUseCase,
    DeleteCalculationUseCase
)
from app.application.dtos.insurance import (
    InsuranceCalculationRequest,
    InsuranceCalculationResponse
)
from app.domain.entities import InsuranceCalculationEntity
from app.domain.exceptions import InvalidCarInfoError, RepositoryError, CalculationNotFoundError
from app.main import get_insurance_repository, get_settings

logger = logging.getLogger(__name__)

# Router 
router = APIRouter(
    prefix="/insurance",
    tags=["insurance"]
)

# Funções de Dependência para Casos de Uso 
def get_calculate_insurance_use_case(
    repository: InsuranceCalculationRepository = Depends(get_insurance_repository),
    app_settings: Settings = Depends(get_settings) 
) -> CalculateInsuranceUseCase:
    return CalculateInsuranceUseCase(repository=repository, app_settings=app_settings)

def get_get_calculation_use_case(
    repository: InsuranceCalculationRepository = Depends(get_insurance_repository)
) -> GetCalculationUseCase:
    return GetCalculationUseCase(repository=repository)

def get_list_calculations_use_case(
    repository: InsuranceCalculationRepository = Depends(get_insurance_repository)
) -> ListCalculationsUseCase:
    return ListCalculationsUseCase(repository=repository)

def get_delete_calculation_use_case(
    repository: InsuranceCalculationRepository = Depends(get_insurance_repository)
) -> DeleteCalculationUseCase:
    return DeleteCalculationUseCase(repository=repository)

# Endpoints 
@router.post(
    "/calculate",
    response_model=InsuranceCalculationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calcula o valor do seguro para um carro",
)
async def calculate_insurance_endpoint(
    request: InsuranceCalculationRequest,
    use_case: CalculateInsuranceUseCase = Depends(get_calculate_insurance_use_case)
) -> InsuranceCalculationResponse:
    try:
        logger.info(f"Cálculo de seguro requisitado para: {request.model_dump()}")
        result: InsuranceCalculationEntity = await use_case.execute(**request.model_dump())
        logger.info(f"Cálculo ID {result.id} concluído com sucesso.")
        return InsuranceCalculationResponse(
            id=str(result.id),
            timestamp=result.created_at,
            car_make=result.car_info.make,
            car_model=result.car_info.model,
            car_year=result.car_info.year,
            car_value=float(result.car_info.value),
            applied_rate=float(result.applied_rate),
            calculated_premium=float(result.calculated_premium.amount),
            deductible_value=float(result.deductible_value.amount),
            policy_limit=float(result.policy_limit.amount),
            gis_adjustment=float(result.gis_adjustment) if result.gis_adjustment is not None else None,
            broker_fee=float(result.broker_fee.amount)
        )
    except InvalidCarInfoError as e:
        logger.warning(f"Erro de validação ao calcular seguro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RepositoryError as e:
        logger.error(f"Erro de repositório ao calcular seguro: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar o cálculo do seguro"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao calcular seguro: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro inesperado ao calcular o seguro"
        )

@router.get(
    "/calculations/{calculation_id}",
    response_model=InsuranceCalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtém um cálculo de seguro pelo ID",
    responses={status.HTTP_404_NOT_FOUND: {"detail": "Cálculo não encontrado"}}
)
async def get_calculation_endpoint(
    calculation_id: str,
    use_case: GetCalculationUseCase = Depends(get_get_calculation_use_case)
) -> InsuranceCalculationResponse:
    try:
        logger.info(f"Buscando cálculo com ID: {calculation_id}")
        result = await use_case.execute(calculation_id)
        
        logger.info(f"Cálculo ID {calculation_id} encontrado.")
        return InsuranceCalculationResponse(
            id=str(result.id),
            timestamp=result.created_at,
            car_make=result.car_info.make,
            car_model=result.car_info.model,
            car_year=result.car_info.year,
            car_value=float(result.car_info.value),
            applied_rate=float(result.applied_rate),
            calculated_premium=float(result.calculated_premium.amount),
            deductible_value=float(result.deductible_value.amount),
            policy_limit=float(result.policy_limit.amount),
            gis_adjustment=float(result.gis_adjustment) if result.gis_adjustment is not None else None,
            broker_fee=float(result.broker_fee.amount)
        )
    except CalculationNotFoundError as e:
        logger.warning(f"Cálculo ID {calculation_id} não encontrado para GET.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cálculo não encontrado"
        )
    except RepositoryError as e:
        logger.error(f"Erro de repositório ao buscar cálculo {calculation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar cálculo"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar cálculo {calculation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar cálculo"
        )

@router.get(
    "/calculations",
    response_model=List[InsuranceCalculationResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista os cálculos de seguro realizados",
)
async def list_calculations_endpoint(
    limit: int = Query(10, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Deslocamento inicial para paginação"),
    use_case: ListCalculationsUseCase = Depends(get_list_calculations_use_case)
) -> List[InsuranceCalculationResponse]:
    try:
        logger.info(f"Listando cálculos com limit={limit}, offset={offset}")
        results = await use_case.execute(limit=limit, offset=offset)
        logger.info(f"{len(results)} cálculos listados.")
        return [
            InsuranceCalculationResponse(
                id=str(result.id),
                timestamp=result.created_at,
                car_make=result.car_info.make,
                car_model=result.car_info.model,
                car_year=result.car_info.year,
                car_value=float(result.car_info.value),
                applied_rate=float(result.applied_rate),
                calculated_premium=float(result.calculated_premium.amount),
                deductible_value=float(result.deductible_value.amount),
                policy_limit=float(result.policy_limit.amount),
                gis_adjustment=float(result.gis_adjustment) if result.gis_adjustment is not None else None,
                broker_fee=float(result.broker_fee.amount)
            ) for result in results
        ]
    except RepositoryError as e:
        logger.error(f"Erro de repositório ao listar cálculos: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar cálculos.")
    except Exception as e:
        logger.error(f"Erro inesperado ao listar cálculos: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno inesperado.")

@router.delete(
    "/calculations/{calculation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marca um cálculo de seguro como deletado (Soft Delete)",
    tags=["insurance"],
    responses={
        status.HTTP_404_NOT_FOUND: {"detail": "Cálculo não encontrado"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"detail": "Erro ao deletar cálculo"}
    }
)
async def delete_calculation_endpoint(
    calculation_id: str,
    use_case: DeleteCalculationUseCase = Depends(get_delete_calculation_use_case)
):
    """Marca um cálculo como deletado usando seu ID."""
    try:
        logger.info(f"Requisição para deletar cálculo ID: {calculation_id}")
        success = await use_case.execute(calculation_id)
        if not success:
            logger.warning(f"Tentativa de deletar cálculo não encontrado ID: {calculation_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cálculo não encontrado")
            
        logger.info(f"Cálculo ID {calculation_id} marcado como deletado.")
        return
        
    except RepositoryError as e:
        logger.error(f"Erro de repositório ao deletar cálculo {calculation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar cálculo.")
    except Exception as e:
        logger.error(f"Erro inesperado ao deletar cálculo {calculation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno inesperado.") 