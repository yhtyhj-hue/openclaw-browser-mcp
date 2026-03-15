import time
import asyncio
import psutil
from fastapi import Request
from app.monitoring.metrics import metrics
from app.monitoring.prometheus_exporter import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    system_memory_bytes,
    system_cpu_usage_percent,
)
from app.monitoring.logger import Loggers

logger = Loggers.get_api_logger()

class MetricsMiddleware:
    """监控中间件"""
    
    def __init__(self, app):
        self.app = app
        self.process = psutil.Process()
    
    async def __call__(self, request: Request, call_next):
        """处理请求并收集指标"""
        
        # 记录开始时间
        start_time = time.time()
        http_requests_in_progress.inc()
        
        # 获取请求信息
        endpoint = request.url.path
        method = request.method
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 更新指标
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_time)
            
            # 记录到本地指标
            metrics.record_request(endpoint, response_time, response.status_code)
            
            # 日志记录
            logger.info(
                f"{method} {endpoint} - {response.status_code} ({response_time:.3f}s)"
            )
            
            return response
            
        except Exception as exc:
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 记录错误
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()
            
            logger.error(
                f"{method} {endpoint} - Error: {str(exc)} ({response_time:.3f}s)"
            )
            
            raise
            
        finally:
            http_requests_in_progress.dec()
            
            # 定期更新系统指标
            if int(time.time()) % 10 == 0:  # 每10秒更新一次
                self._update_system_metrics()
    
    def _update_system_metrics(self):
        """更新系统指标"""
        try:
            # CPU 使用率
            cpu_percent = self.process.cpu_percent(interval=0.1)
            system_cpu_usage_percent.set(cpu_percent)
            
            # 内存使用情况
            mem_info = self.process.memory_info()
            system_memory_bytes.labels(type='resident').set(mem_info.rss)
            system_memory_bytes.labels(type='virtual').set(mem_info.vms)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")