from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_chinese_status_message():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "稻田智研平台后端服务运行正常",
    }
