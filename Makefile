.PHONY: help build up down logs test clean lint install

help:
	@echo "🚀 OpenClaw Browser MCP Server - 可用命令"
	@echo ""
	@echo "安装相关:"
	@echo "  make install         - 安装Python依赖"
	@echo "  make install-browser - 安装Playwright浏览器"
	@echo ""
	@echo "开发相关:"
	@echo "  make dev             - 开发模式运行"
	@echo "  make test            - 运行单元测试"
	@echo "  make lint            - 代码检查"
	@echo ""
	@echo "Docker相关:"
	@echo "  make build           - 构建Docker镜像"
	@echo "  make up              - 启动Docker容器"
	@echo "  make down            - 停止Docker容器"
	@echo "  make logs            - 查看Docker日志"
	@echo "  make ps              - 查看容器状态"
	@echo ""
	@echo "清理相关:"
	@echo "  make clean           - 清理临时文件"
	@echo "  make clean-all       - 完全清理"
	@echo ""

install:
	pip install -r requirements.txt

install-browser:
	playwright install chromium

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	black app/
	flake8 app/

build:
	docker build -t openclaw-browser-mcp:latest .

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage

clean-all: clean
	docker-compose down -v
	rm -rf logs/*
	docker rmi openclaw-browser-mcp:latest

.PHONY: all