# 🚀 OpenClaw Browser MCP Server - 部署指南

## 目录

1. [快速开始](#快速开始)
2. [本地开发环境](#本地开发环境)
3. [Docker 容器化](#docker-容器化)
4. [生产环境部署](#生产环境部署)
5. [Nginx 反向代理](#nginx-反向代理)
6. [性能优化](#性能优化)
7. [监控和日志](#监控和日志)
8. [故障排除](#故障排除)
9. [安全加固](#安全加固)

---

## 🏃 快速开始

### 最快速的本地运行方式

```bash
# 1. 克隆项目
git clone https://github.com/yhtyhj-hue/openclaw-browser-mcp.git
cd openclaw-browser-mcp

# 2. 使用 Docker Compose 一键启动（推荐）
docker-compose up -d

# 3. 验证服务状态
curl http://localhost:8000/health

# 4. 查看 API 文档
浏览器访问: http://localhost:8000/api/docs
```

**就这么简单！** ✨

---

## 💻 本地开发环境

### 系统要求

- **操作系统**: Linux, macOS, Windows (WSL2)
- **Python**: 3.11+
- **内存**: 4GB+ (浏览器进程耗内存)
- **磁盘**: 5GB+ (Playwright 浏览器)

### 详细安装步骤

#### 1. 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip git

# macOS
brew install python@3.11

# Windows
# 从 python.org 下载 Python 3.11 安装程序
```

#### 2. 克隆和配置

```bash
git clone https://github.com/yhtyhj-hue/openclaw-browser-mcp.git
cd openclaw-browser-mcp

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 文件配置参数
```

#### 3. 本地运行

```bash
# 开发模式 (自动重启)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接运行
python -m app.main
```

#### 4. 验证安装

```bash
# 在另一个终端测试
curl http://localhost:8000/health

# 应返回:
# {
#   "status": "healthy",
#   "timestamp": "2026-03-14T..."
# }
```

---

## 🐳 Docker 容器化

### 构建 Docker 镜像

```bash
# 构建镜像
docker build -t openclaw-browser-mcp:latest .

# 标记版本
docker tag openclaw-browser-mcp:latest openclaw-browser-mcp:1.0.0
docker tag openclaw-browser-mcp:latest your-registry/openclaw-browser-mcp:latest

# 推送到镜像仓库（可选）
docker push your-registry/openclaw-browser-mcp:latest
```

### 单容器运行

```bash
# 运行容器
docker run -d \
  --name openclaw-browser-mcp \
  -p 8000:8000 \
  -e SERVER_HOST=0.0.0.0 \
  -e SERVER_PORT=8000 \
  -e BROWSER_TIMEOUT=30000 \
  -v ./logs:/app/logs \
  openclaw-browser-mcp:latest

# 查看日志
docker logs -f openclaw-browser-mcp

# 停止容器
docker stop openclaw-browser-mcp

# 删除容器
docker rm openclaw-browser-mcp
```

### Docker Compose 部署（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f openclaw-browser-mcp

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

---

## 🌍 生产环境部署

### 推荐架构

```
┌─────────────────────────────────────────────────┐
│                  Internet                        │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│           Nginx 反向代理 (Port 80/443)          │
│              负载均衡 + SSL/TLS                   │
└─────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ App 1   │    │ App 2   │    │ App 3   │
   │ :8000   │    │ :8001   │    │ :8002   │
   └─────────┘    └─────────┘    └─────────┘
        ↓               ↓               ↓
   ┌─────────────────────────────────────┐
   │      Redis 缓存 (可选)              │
   └─────────────────────────────────────┘
```

### 使用 Docker Compose (完整生产配置)

创建 `docker-compose.prod.yml`:

```yaml
version: '3.9'

services:
  nginx:
    image: nginx:alpine
    container_name: openclaw-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - app1
      - app2
    restart: always
    networks:
      - openclaw-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  app1:
    image: openclaw-browser-mcp:latest
    container_name: openclaw-app1
    environment:
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
      - ENVIRONMENT=production
      - DEBUG=False
      - LOG_LEVEL=INFO
      - BROWSER_TIMEOUT=30000
      - MAX_SESSIONS=5
    volumes:
      - ./logs/app1:/app/logs
    restart: always
    networks:
      - openclaw-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  app2:
    image: openclaw-browser-mcp:latest
    container_name: openclaw-app2
    environment:
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8001
      - ENVIRONMENT=production
      - DEBUG=False
      - LOG_LEVEL=INFO
      - BROWSER_TIMEOUT=30000
      - MAX_SESSIONS=5
    volumes:
      - ./logs/app2:/app/logs
    restart: always
    networks:
      - openclaw-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: openclaw-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: always
    networks:
      - openclaw-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  openclaw-network:
    driver: bridge

volumes:
  redis-data:
```

启动生产环境:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 Nginx 反向代理

### Nginx 配置文件

创建 `nginx.conf`:

```nginx
# 上游服务器定义
upstream openclaw_app {
    # 负载均衡策略
    least_conn;  # 最少连接
    
    server app1:8000 max_fails=3 fail_timeout=30s;
    server app2:8001 max_fails=3 fail_timeout=30s;
    
    keepalive 32;
}

# 速率限制定义
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=100r/m;

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name openclaw.example.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS 主服务器
server {
    listen 443 ssl http2;
    server_name openclaw.example.com;
    
    # SSL 证书 (使用 Let's Encrypt)
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL 最佳实践
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头部
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # 日志
    access_log /var/log/nginx/access.log combined buffer=32k;
    error_log /var/log/nginx/error.log warn;
    
    # 性能优化
    client_max_body_size 10M;
    proxy_cache_bypass $http_upgrade;
    
    # 健康检查端点
    location /health {
        access_log off;
        proxy_pass http://openclaw_app;
    }
    
    # API 端点（有速率限制）
    location /session {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://openclaw_app;
        proxy_http_version 1.1;
        
        # 代理头部
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # 连接设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
        
        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 通用代理
    location / {
        limit_req zone=general_limit burst=10 nodelay;
        
        proxy_pass http://openclaw_app;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 使用 Let's Encrypt 配置 SSL

```bash
# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 生成证书
sudo certbot certonly --standalone -d openclaw.example.com

# 证书位置
# /etc/letsencrypt/live/openclaw.example.com/fullchain.pem
# /etc/letsencrypt/live/openclaw.example.com/privkey.pem

# 自动续期
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Docker 中的 SSL 支持

```bash
# 创建 SSL 目录
mkdir -p ssl

# 复制证书
cp /etc/letsencrypt/live/openclaw.example.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/openclaw.example.com/privkey.pem ssl/key.pem

# 修改权限
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem

# Docker Compose 会自动挂载这些文件
```

---

## ⚡ 性能优化

### 1. 浏览器进程优化

编辑 `.env`:

```env
# 启用无头模式（更快）
HEADLESS=True

# 增加浏览器超时
BROWSER_TIMEOUT=60000

# 限制并发会话
MAX_SESSIONS=10

# 禁用自动化检测标记
DISABLE_AUTOMATION=True
```

### 2. Docker 资源限制

编辑 `docker-compose.yml`:

```yaml
services:
  app1:
    image: openclaw-browser-mcp:latest
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 3. 优化 Dockerfile

使用多阶段构建减小镜像大小:

```dockerfile
# 缓存优化
FROM python:3.11-slim as base

# 依赖层
FROM base as dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

# 最终层
FROM dependencies
COPY . .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. 启用 Gzip 压缩

在 Nginx 配置中添加:

```nginx
gzip on;
gzip_min_length 1000;
gzip_proxied any;
gzip_types text/plain text/css text/xml text/javascript 
           application/x-javascript application/xml+rss 
           application/json application/javascript;
```

---

## 📊 监控和日志

### 1. 日志配置

编辑 `.env`:

```env
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 2. Docker 日志驱动

在 `docker-compose.yml` 中配置:

```yaml
services:
  app1:
    image: openclaw-browser-mcp:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "openclaw-app"
```

### 3. 集中日志收集（ELK Stack）

创建 `docker-compose.elk.yml`:

```yaml
version: '3'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.0.0
    volumes:
      - ./logs:/logs:ro
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml
    depends_on:
      - elasticsearch
```

### 4. 性能监控

启用 Prometheus 指标:

```bash
# 安装依赖
pip install prometheus-client

# 在应用中使用 (app/main.py)
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

---

## 🛠️ 故障排除

### 1. 浏览器启动失败

```bash
# 检查 Playwright 是否正确安装
playwright install

# 检查系统依赖
sudo apt-get install -y libwdl-core1 libx11-6 libxcb1 libxdamage1

# 使用有头模式调试
HEADLESS=False docker-compose up
```

### 2. 连接超时

```bash
# 检查网络连接
docker-compose ps
docker network ls

# 增加超时时间
BROWSER_TIMEOUT=60000
```

### 3. 内存泄漏

```bash
# 监控内存使用
docker stats openclaw-app1

# 限制内存
memory: 2G
memory_swap: 2G
```

### 4. 验证码识别失败

```bash
# 检查 OCR 依赖
tesseract --version

# 检查 2Captcha API
curl -X GET "https://2captcha.com/api/user?apikey=YOUR_KEY&action=getbalance"
```

---

## 🔒 安全加固

### 1. 防火墙配置

```bash
# 仅允许必要的端口
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. 隐藏服务版本信息

编辑 `nginx.conf`:

```nginx
server_tokens off;
add_header Server "Secured" always;
```

### 3. 限制请求大小

编辑 `.env`:

```env
CLIENT_MAX_BODY_SIZE=10M
```

### 4. API 认证

编辑 `app/config.py`:

```python
# 添加 API 密钥认证
API_KEY_ENABLED=True
API_KEYS=["key1", "key2"]
```

### 5. CORS 配置

编辑 `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-domain.com"],  # 改为具体域名
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

## 📋 检查清单

部署前必检:

- [ ] 环境变量配置正确 (.env 文件)
- [ ] SSL 证书已配置 (生产环境)
- [ ] 日志目录已创建和权限正确
- [ ] Docker 镜像已构建和测试
- [ ] Nginx 配置已验证 (`nginx -t`)
- [ ] 防火墙规则已配置
- [ ] 备份策略已制定
- [ ] 监控告警已配置
- [ ] 性能基准已建立
- [ ] 灾难恢复计划已准备

---

## 📞 支持

有问题？查看：
- API 文档: http://localhost:8000/api/docs
- 日志文件: `./logs/app.log`
- GitHub Issues: https://github.com/yhtyhj-hue/openclaw-browser-mcp/issues

---

**祝你部署顺利！** 🎉