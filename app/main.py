import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.logger import setup_logger
from app.browser.browser_manager import BrowserManager
from app.monitoring.middleware import MetricsMiddleware
from app.monitoring import routes as monitoring_routes
from app.api import (
    health_routes,
    session_routes,
    browser_routes,
    captcha_routes,
    content_routes,
    interaction_routes,
    advanced_routes,
    workflow_routes,
)

logger = setup_logger(__name__)
browser_manager: BrowserManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global browser_manager
    
    logger.info("=" * 60)
    logger.info("🚀 Starting OpenClaw Browser MCP Server...")
    logger.info("=" * 60)
    
    browser_manager = BrowserManager(max_sessions=settings.max_sessions)
    await browser_manager.initialize()
    
    logger.info(f"✅ Server started successfully!")
    logger.info(f"📡 Listening on {settings.server_host}:{settings.server_port}")
    logger.info(f"📊 Max sessions: {settings.max_sessions}")
    logger.info(f"📈 Metrics available at /metrics")
    logger.info(f"❤️ Health check at /health")
    logger.info("=" * 60)
    
    yield
    
    logger.info("=" * 60)
    logger.info("🛑 Shutting down server...")
    logger.info("=" * 60)
    
    await browser_manager.cleanup()
    logger.info("✅ Server shut down successfully")

# 创建 FastAPI 应用
app = FastAPI(
    title="OpenClaw Browser MCP Server",
    description="为 OpenClaw AI 提供浏览器自动化、页面理解、验证码识别的 MCP 服务",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 监控中间件（记录请求指标）
app.add_middleware(MetricsMiddleware)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求"""
    logger.debug(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response

# 异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理验证错误"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Invalid request parameters",
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理全局异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "detail": "Internal server error",
        },
    )

# 注册路由
app.include_router(monitoring_routes.router, prefix="/", tags=["📊 Monitoring"])
app.include_router(health_routes.router, tags=["📊 Health"])
app.include_router(session_routes.router, prefix="/session", tags=["🔌 Session Management"])
app.include_router(browser_routes.router, prefix="/session", tags=["🌐 Browser Operations"])
app.include_router(captcha_routes.router, prefix="/session", tags=["🔐 Captcha Handling"])
app.include_router(content_routes.router, prefix="/session", tags=["📄 Content Extraction"])
app.include_router(interaction_routes.router, prefix="/session", tags=["🖱️ Interaction"])
app.include_router(advanced_routes.router, prefix="/session", tags=["⚙️ Advanced Features"])
app.include_router(workflow_routes.router, prefix="/session", tags=["⚡ Workflows"])

# API 信息
@app.get("/api/info")
async def api_info():
    """获取API信息和统计"""
    return {
        "name": "OpenClaw Browser MCP Server",
        "version": "1.0.0",
        "status": "operational",
        "active_sessions": browser_manager.get_active_sessions_count() if browser_manager else 0,
        "max_sessions": settings.max_sessions,
        "environment": settings.environment,
        "debug": settings.debug,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower(),
    )