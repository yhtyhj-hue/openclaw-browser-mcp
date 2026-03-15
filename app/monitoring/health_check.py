import asyncio
from typing import Dict, Any
from datetime import datetime
from app.monitoring.logger import Loggers

logger = Loggers.get_app_logger()

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.last_check = None
        self.check_interval = 30  # 秒
    
    async def check(self) -> Dict[str, Any]:
        """执行健康检查"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {}
            }
            
            # 检查浏览器管理器
            try:
                browser_check = await self._check_browser()
                health_status["checks"]["browser"] = browser_check
                if not browser_check["status"] == "ok":
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["checks"]["browser"] = {
                    "status": "error",
                    "message": str(e)
                }
                health_status["status"] = "unhealthy"
            
            # 检查会话管理
            try:
                session_check = await self._check_sessions()
                health_status["checks"]["sessions"] = session_check
            except Exception as e:
                health_status["checks"]["sessions"] = {
                    "status": "error",
                    "message": str(e)
                }
                health_status["status"] = "unhealthy"
            
            # 检查内存
            try:
                memory_check = await self._check_memory()
                health_status["checks"]["memory"] = memory_check
                if memory_check["status"] != "ok":
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["checks"]["memory"] = {
                    "status": "error",
                    "message": str(e)
                }
            
            self.last_check = health_status
            logger.info(f"Health check completed: {health_status['status']}")
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_browser(self) -> Dict[str, Any]:
        """检查浏览器状态"""
        try:
            if not self.browser_manager or not self.browser_manager.browser:
                return {"status": "error", "message": "Browser not initialized"}
            
            return {
                "status": "ok",
                "browser": "chromium",
                "version": "latest"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _check_sessions(self) -> Dict[str, Any]:
        """检查会话状态"""
        try:
            active_sessions = self.browser_manager.get_active_sessions_count()
            max_sessions = self.browser_manager.max_sessions
            
            if active_sessions > max_sessions * 0.9:
                status = "warning"
            else:
                status = "ok"
            
            return {
                "status": status,
                "active": active_sessions,
                "max": max_sessions,
                "utilization": (active_sessions / max_sessions) * 100
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _check_memory(self) -> Dict[str, Any]:
        """检查内存使用"""
        try:
            import psutil
            
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            
            if mem_percent > 90:
                status = "critical"
            elif mem_percent > 75:
                status = "warning"
            else:
                status = "ok"
            
            return {
                "status": status,
                "used_percent": mem_percent,
                "available_gb": mem.available / (1024**3),
                "total_gb": mem.total / (1024**3)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}