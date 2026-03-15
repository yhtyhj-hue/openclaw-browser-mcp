from typing import Callable, List, Dict, Any
from enum import Enum
from datetime import datetime
from app.monitoring.logger import Loggers

logger = Loggers.get_app_logger()

class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Alert:
    """告警信息"""
    
    def __init__(self, level: AlertLevel, title: str, message: str, details: Dict[str, Any] = None):
        self.level = level
        self.title = title
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class AlertHandler:
    """告警处理器"""
    
    def __init__(self):
        self.handlers: List[Callable] = []
        self.alert_history: List[Alert] = []
        self.max_history = 1000
    
    def add_handler(self, handler: Callable):
        """添加告警处理器"""
        self.handlers.append(handler)
    
    def trigger_alert(self, alert: Alert):
        """触发告警"""
        self.alert_history.append(alert)
        
        # 限制历史记录大小
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # 记录日志
        log_level = alert.level.value
        logger.log(
            getattr(logging, log_level),
            f"[{alert.level.value}] {alert.title}: {alert.message}"
        )
        
        # 调用所有处理器
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def get_alerts(self, level: AlertLevel = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取告警历史"""
        alerts = self.alert_history
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return [a.to_dict() for a in alerts[-limit:]]

# 全局告警处理器
alert_handler = AlertHandler()

def email_alert_handler(alert: Alert):
    """邮件告警处理器"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # TODO: 配置邮件参数
        logger.info(f"Sending email alert: {alert.title}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")

def webhook_alert_handler(alert: Alert):
    """Webhook 告警处理器"""
    try:
        import requests
        # TODO: 配置 Webhook URL
        # requests.post(webhook_url, json=alert.to_dict())
        logger.info(f"Sending webhook alert: {alert.title}")
    except Exception as e:
        logger.error(f"Failed to send webhook alert: {e}")

# 注册默认处理器
# alert_handler.add_handler(email_alert_handler)
# alert_handler.add_handler(webhook_alert_handler)