from fastapi import APIRouter, HTTPException
from app.monitoring.metrics import metrics
from app.monitoring.health_check import HealthChecker
from app.monitoring.alerts import alert_handler
from app.main import browser_manager
from app.logger import setup_logger
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

logger = setup_logger(__name__)
router = APIRouter()

# 创建健康检查器
health_checker = None

@router.get("/health", tags=["Monitoring"])
async def health_check():
    """服务健康检查"""
    global health_checker
    
    if not health_checker and browser_manager:
        health_checker = HealthChecker(browser_manager)
    
    if health_checker:
        return await health_checker.check()
    else:
        return {"status": "initializing"}

@router.get("/metrics", tags=["Monitoring"])
async def metrics_endpoint():
    """Prometheus 格式的指标"""
    try:
        metrics_output = generate_latest()
        return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", tags=["Monitoring"])
async def get_stats():
    """获取应用统计信息"""
    try:
        stats = metrics.get_stats()
        
        if browser_manager:
            stats["browser"] = {
                "active_sessions": browser_manager.get_active_sessions_count(),
                "max_sessions": browser_manager.max_sessions,
            }
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts", tags=["Monitoring"])
async def get_alerts(level: str = None, limit: int = 100):
    """获取告警历史"""
    try:
        alerts = alert_handler.get_alerts(limit=limit)
        return {
            "status": "success",
            "count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/reset", tags=["Monitoring"])
async def reset_metrics():
    """重置指标（仅开发用）"""
    try:
        metrics.reset()
        return {"status": "success", "message": "Metrics reset"}
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))