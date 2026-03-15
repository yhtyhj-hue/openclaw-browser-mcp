from prometheus_client import Counter, Histogram, Gauge
import time

# ==================== 请求相关指标 ====================

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress'
)

# ==================== 浏览器相关指标 ====================

browser_sessions_active = Gauge(
    'browser_sessions_active',
    'Active browser sessions'
)

browser_sessions_total = Counter(
    'browser_sessions_total',
    'Total browser sessions created'
)

browser_navigation_duration_seconds = Histogram(
    'browser_navigation_duration_seconds',
    'Browser navigation latency',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

# ==================== 验证码相关指标 ====================

captcha_detections_total = Counter(
    'captcha_detections_total',
    'Total CAPTCHA detections',
    ['type']
)

captcha_solutions_total = Counter(
    'captcha_solutions_total',
    'Total CAPTCHA solutions',
    ['type', 'result']  # result: success, failed
)

captcha_solution_duration_seconds = Histogram(
    'captcha_solution_duration_seconds',
    'CAPTCHA solution time',
    ['type']
)

# ==================== 内容提取相关指标 ====================

content_extraction_duration_seconds = Histogram(
    'content_extraction_duration_seconds',
    'Content extraction latency',
    ['content_type']  # text, links, forms, tables, etc.
)

# ==================== 系统相关指标 ====================

system_errors_total = Counter(
    'system_errors_total',
    'Total system errors',
    ['error_type']
)

system_memory_bytes = Gauge(
    'system_memory_bytes',
    'System memory usage',
    ['type']  # resident, virtual
)

system_cpu_usage_percent = Gauge(
    'system_cpu_usage_percent',
    'CPU usage percentage'
)