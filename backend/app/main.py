from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="稻田智研平台后端服务")
app.include_router(api_router)
