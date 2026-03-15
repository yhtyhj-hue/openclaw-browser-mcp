# OpenClaw Browser MCP Server

为 OpenClaw AI 提供浏览器自动化、页面理解、验证码识别的 MCP 服务（RESTful API）。

## 功能概览

- **浏览器自动化**：基于 Playwright，多会话、导航、点击、输入、截图、执行脚本等
- **验证码处理**：图片/滑块/reCAPTCHA 等检测与求解（见 [CAPTCHA_HANDLING.md](CAPTCHA_HANDLING.md)）
- **内容提取**：链接、图片、表单、表格、结构化提取
- **监控与日志**：Prometheus 指标、健康检查（见 [MONITORING.md](MONITORING.md)）
- **API 文档**：启动后访问 `/api/docs`（Swagger）、`/api/redoc`

## 快速开始

### 环境要求

| 项目     | 要求 |
|----------|------|
| Python   | 3.11 或 3.12 推荐（3.13 见 [INSTALLATION.md](INSTALLATION.md)） |
| 内存/磁盘 | 4GB+ / 5GB+（含浏览器） |

### 本地运行

```bash
# 克隆后进入项目目录
cd openclaw-browser-mcp

# 虚拟环境 + 依赖
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# 启动服务（默认 http://0.0.0.0:8000）
make dev
# 或: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：`curl http://localhost:8000/health`  
API 文档：http://localhost:8000/api/docs

### Docker 部署

生产与监控编排见 [DEPLOYMENT.md](DEPLOYMENT.md)，使用 `docker-compose.prod.yml`、`docker-compose.monitoring.yml` 等。

```bash
# 示例：生产编排
docker-compose -f docker-compose.prod.yml up -d
```

## 项目结构

```
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── api/             # 路由（健康、会话、浏览器、验证码、内容、交互、高级、工作流）
│   ├── browser/         # 浏览器会话管理
│   ├── captcha/         # 验证码检测与求解
│   ├── content/         # 内容提取
│   └── monitoring/      # 指标与中间件
├── requirements.txt
├── Makefile             # make help 查看命令
├── API.md               # 接口说明
├── INSTALLATION.md      # 安装与系统要求
├── DEPLOYMENT.md        # 部署与编排
├── CAPTCHA_HANDLING.md  # 验证码处理说明
└── MONITORING.md        # 监控与告警
```

## 常用命令（Makefile）

| 命令 | 说明 |
|------|------|
| `make install` | 安装 Python 依赖 |
| `make install-browser` | 安装 Playwright 浏览器（chromium） |
| `make dev` | 开发模式运行（端口 8000） |
| `make test` | 运行测试 |
| `make lint` | 代码检查（black + flake8） |

## 文档索引

- [INSTALLATION.md](INSTALLATION.md) — 安装与环境配置
- [API.md](API.md) — 完整 API 说明（40+ 端点）
- [DEPLOYMENT.md](DEPLOYMENT.md) — 生产部署与 Docker 编排
- [CAPTCHA_HANDLING.md](CAPTCHA_HANDLING.md) — 验证码处理
- [MONITORING.md](MONITORING.md) — 监控与 Grafana/ELK

## 技术栈

Python 3.11+ · FastAPI · Playwright · OpenCV · Tesseract · Prometheus · Docker
