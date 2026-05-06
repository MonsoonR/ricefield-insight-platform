from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services.health import get_health_status

router = APIRouter(tags=["系统状态"])


@router.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    return get_health_status()
