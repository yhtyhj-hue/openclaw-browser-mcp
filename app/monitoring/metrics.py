import time
from datetime import datetime
from typing import Dict, Any, Optional
from collections import defaultdict
import asyncio
from app.monitoring.logger import Loggers

logger = Loggers.get_performance_logger()

class Metrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.request_times: Dict[str, list] = defaultdict(list)
        self.browser_sessions_peak = 0
        self.captcha_attempts = 0
        self.captcha_successes = 0
        self.session_start_time = datetime.utcnow()
    
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """记录请求"""
        self.request_count += 1
        self.total_response_time += response_time
        self.request_times[endpoint].append(response_time)
        
        if status_code >= 400:
            self.error_count += 1
        
        logger.info(
            f"Request recorded",
            extra={
                "endpoint": endpoint,
                "response_time": response_time,
                "status_code": status_code,
            }
        )
    
    def record_captcha_attempt(self, success: bool):
        """记录验证码尝试"""
        self.captcha_attempts += 1
        if success:
            self.captcha_successes += 1
    
    def get_average_response_time(self, endpoint: Optional[str] = None) -> float:
        """获取平均响应时间"""
        if not self.request_count:
            return 0.0
        
        if endpoint:
            times = self.request_times.get(endpoint, [])
            return sum(times) / len(times) if times else 0.0
        
        return self.total_response_time / self.request_count
    
    def get_captcha_success_rate(self) -> float:
        """获取验证码成功率"""
        if not self.captcha_attempts:
            return 0.0
        return (self.captcha_successes / self.captcha_attempts) * 100
    
    def get_stats(self) -> Dict[str, Any]:
        """获取所有统计信息"""
        uptime = (datetime.utcnow() - self.session_start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "average_response_time_ms": self.get_average_response_time() * 1000,
            "requests_per_minute": (self.request_count / (uptime / 60)) if uptime > 0 else 0,
            "captcha_attempts": self.captcha_attempts,
            "captcha_successes": self.captcha_successes,
            "captcha_success_rate": self.get_captcha_success_rate(),
            "endpoint_stats": {
                endpoint: {
                    "count": len(times),
                    "avg_time_ms": (sum(times) / len(times) * 1000) if times else 0,
                    "min_time_ms": min(times) * 1000 if times else 0,
                    "max_time_ms": max(times) * 1000 if times else 0,
                }
                for endpoint, times in self.request_times.items()
            }
        }
    
    def reset(self):
        """重置指标"""
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.request_times.clear()
        self.captcha_attempts = 0
        self.captcha_successes = 0
        self.session_start_time = datetime.utcnow()

# 全局指标实例
metrics = Metrics()