# 📊 监控和日志系统

## 目录

1. [日志系统](#日志系统)
2. [性能指标](#性能指标)
3. [健康检查](#健康检查)
4. [告警系统](#告警系统)
5. [Prometheus 集成](#prometheus-集成)
6. [ELK 集成](#elk-集成)
7. [最佳实践](#最佳实践)

---

## 📝 日志系统

### 日志级别

| 级别 | 说明 | 用途 |
|------|------|------|
| DEBUG | 调试信息 | 开发调试 |
| INFO | 普通信息 | 正常操作流程 |
| WARNING | 警告信息 | 潜在问题 |
| ERROR | 错误信息 | 明确的错误 |
| CRITICAL | 严重错误 | 系统崩溃风险 |

### 配置日志

编辑 `.env`:

```env
# 日志级别
LOG_LEVEL=INFO

# 日志文件位置
LOG_FILE=logs/app.log

# 日志格式 (json 或 text)
LOG_FORMAT=json
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看 JSON 格式日志
cat logs/app.log | jq '.message'

# 按级别过滤
grep "ERROR" logs/app.log
```

### 日志示例

```json
{
  "timestamp": "2026-03-14T10:30:00.000000",
  "level": "INFO",
  "logger": "app.api",
  "message": "POST /session/open - 200 (0.123s)"
}
```

---

## 📈 性能指标

### API 端点

#### `/stats` - 获取应用统计

```bash
curl http://localhost:8000/stats
```

**响应:**

```json
{
  "status": "success",
  "stats": {
    "uptime_seconds": 3600,
    "total_requests": 1234,
    "total_errors": 5,
    "error_rate": 0.40,
    "average_response_time_ms": 45.3,
    "requests_per_minute": 20.6,
    "captcha_attempts": 45,
    "captcha_successes": 43,
    "captcha_success_rate": 95.56,
    "endpoint_stats": {
      "/session/open": {
        "count": 234,
        "avg_time_ms": 32.1,
        "min_time_ms": 10.2,
        "max_time_ms": 156.8
      }
    },
    "browser": {
      "active_sessions": 3,
      "max_sessions": 10
    }
  }
}
```

#### `/metrics` - Prometheus 格式指标

```bash
curl http://localhost:8000/metrics
```

**输出:**

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/session/open",method="POST",status="200"} 234.0

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/session/open",method="POST",le="0.01"} 45.0
```

---

## ❤️ 健康检查

### 快速检查

```bash
curl http://localhost:8000/health
```

**健康响应:**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-14T10:30:00.000000",
  "checks": {
    "browser": {
      "status": "ok",
      "browser": "chromium"
    },
    "sessions": {
      "status": "ok",
      "active": 2,
      "max": 10,
      "utilization": 20.0
    },
    "memory": {
      "status": "ok",
      "used_percent": 45.2,
      "available_gb": 6.5,
      "total_gb": 16.0
    }
  }
}
```

### 健康状态

| 状态 | 说明 |
|------|------|
| healthy | 一切正常 |
| degraded | 存在问题但仍可用 |
| unhealthy | 服务不可用 |

---

## 🚨 告警系统

### 告警等级

| 等级 | 含义 | 示例 |
|------|------|------|
| INFO | 信息 | 服务启动 |
| WARNING | 警告 | 内存使用 > 75% |
| ERROR | 错误 | 验证码识别失败 |
| CRITICAL | 严重 | 内存用尽、服务崩溃 |

### 获取告警历史

```bash
curl http://localhost:8000/alerts?limit=50
```

### 配置告警通知

编辑 `app/monitoring/alerts.py`:

```python
# 邮件通知
alert_handler.add_handler(email_alert_handler)

# Webhook 通知
alert_handler.add_handler(webhook_alert_handler)
```

---

## 🔥 Prometheus 集成

### 安装 Prometheus

```bash
# Docker 方式
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Prometheus 配置

创建 `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'openclaw-browser-mcp'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### 查询指标

访问 http://localhost:9090

**常用查询:**

```promql
# 请求速率
rate(http_requests_total[1m])

# 平均响应时间
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# 活跃会话数
browser_sessions_active

# 验证码成功率
rate(captcha_solutions_total{result="success"}[5m]) / rate(captcha_solutions_total[5m])
```

---

## 🔍 ELK 集成 (可选)

### 启动 ELK Stack

```bash
docker-compose -f docker-compose.elk.yml up -d
```

### Filebeat 配置

创建 `filebeat.yml`:

```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /logs/app.log
  json.message_key: message
  json.keys_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
```

### 访问 Kibana

访问 http://localhost:5601

---

## 📊 Grafana 仪表板

### 安装 Grafana

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

访问 http://localhost:3000

### 创建数据源

1. 配置 → 数据源
2. 添加 Prometheus: http://prometheus:9090

### 常用仪表板指标

```json
{
  "panels": [
    {
      "title": "请求速率 (req/s)",
      "targets": [
        {
          "expr": "rate(http_requests_total[1m])"
        }
      ]
    },
    {
      "title": "平均响应时间 (ms)",
      "targets": [
        {
          "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]) * 1000"
        }
      ]
    },
    {
      "title": "活跃会话数",
      "targets": [
        {
          "expr": "browser_sessions_active"
        }
      ]
    },
    {
      "title": "错误率 (%)",
      "targets": [
        {
          "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100"
        }
      ]
    }
  ]
}
```

---

## 📋 最佳实践

### ✅ 建议做法

1. **定期查看日志** - 每日检查错误日志
2. **设置告警阈值** - 内存 75%, CPU 80% 等
3. **保留日志历史** - 至少 30 天
4. **监控关键指标** - 响应时间、错误率、会话数
5. **使用仪表板** - 可视化监控

### ❌ 避免做法

1. ❌ 不要忽视错误日志
2. ❌ 不要设置过严格的告警
3. ❌ 不要定期手动清理日志（应自动化）
4. ❌ 不要在生产环境使用 DEBUG 级别
5. ❌ 不要存储敏感数据到日志

---

## 🔧 故障排除

### 问题: 日志文件很大

**解决方案:**

```bash
# 使用日志轮转
# 编辑 /etc/logrotate.d/openclaw

/app/logs/app.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root root
}
```

### 问题: Prometheus 内存占用高

**解决方案:**

```yaml
# prometheus.yml
global:
  scrape_interval: 30s  # 增加采样间隔
  
retention:
  time: 15d  # 减少保留时间
```

### 问题: 看不到指标

**解决方案:**

```bash
# 检查 Prometheus 是否正确采集
curl http://localhost:8000/metrics

# 检查 Prometheus targets
curl http://localhost:9090/api/v1/targets
```

---

## 📞 支持

- 📚 Prometheus 文档: https://prometheus.io/docs
- 📚 Grafana 文档: https://grafana.com/docs
- 📚 ELK 文档: https://www.elastic.co/guide/index.html