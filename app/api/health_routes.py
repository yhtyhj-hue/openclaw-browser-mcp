from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """服务健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }

@router.get("/", tags=["Health"])
async def root():
    """根路由"""
    return {
        "name": "OpenClaw Browser MCP Server",
        "version": "1.0.0",
        "status": "running",
    }