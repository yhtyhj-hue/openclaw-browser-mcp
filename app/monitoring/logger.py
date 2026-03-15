import logging
import json
from datetime import datetime
from pathlib import Path
from pythonjsonlogger import jsonlogger
from app.config import settings

class JSONFormatter(jsonlogger.JsonFormatter):
    """自定义JSON格式化器"""
    def add_fields(self, log_record, record, message_dict):
        super(JSONFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

def setup_logger(name: str, log_level: str = None) -> logging.Logger:
    """
    配置日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别
    
    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    
    if log_level is None:
        log_level = settings.log_level
    
    logger.setLevel(getattr(logging, log_level))
    
    # 避免重复处理
    if logger.hasHandlers():
        return logger
    
    # 创建日志目录
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== 文件处理器 ====================
    
    if settings.log_format.lower() == 'json':
        # JSON 格式文件日志
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(JSONFormatter())
    else:
        # 纯文本格式文件日志
        file_handler = logging.FileHandler(settings.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
    
    file_handler.setLevel(getattr(logging, log_level))
    logger.addHandler(file_handler)
    
    # ==================== 控制台处理器 ====================
    
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level))
    logger.addHandler(console_handler)
    
    # ==================== 错误文件处理器 ====================
    
    error_log_file = log_dir / 'error.log'
    error_handler = logging.FileHandler(error_log_file)
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)
    
    return logger

# 为各个模块创建专用日志记录器
class Loggers:
    """日志记录器容器"""
    
    @staticmethod
    def get_app_logger():
        return setup_logger('app')
    
    @staticmethod
    def get_browser_logger():
        return setup_logger('app.browser')
    
    @staticmethod
    def get_captcha_logger():
        return setup_logger('app.captcha')
    
    @staticmethod
    def get_api_logger():
        return setup_logger('app.api')
    
    @staticmethod
    def get_performance_logger():
        return setup_logger('app.performance')