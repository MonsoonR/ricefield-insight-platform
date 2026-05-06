from app.schemas.health import HealthResponse


def get_health_status() -> HealthResponse:
    return HealthResponse(
        status="ok",
        message="稻田智研平台后端服务运行正常",
    )
