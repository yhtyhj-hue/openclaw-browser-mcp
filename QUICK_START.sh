#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OpenClaw Browser MCP Server${NC}"
echo -e "${BLUE}  快速开始脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装，请先安装 Git${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git 已安装${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker 未安装（可选，但推荐安装以使用容器化部署）${NC}"
else
    echo -e "${GREEN}✓ Docker 已安装${NC}"
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python3 未安装（本地运行需要）${NC}"
else
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓ Python3 已安装 (版本: $PYTHON_VERSION)${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  初始化步骤${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 配置环境变量
echo -e "${YELLOW}[1/5] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ 已创建 .env 文件${NC}"
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

# 2. 创建日志目录
echo -e "${YELLOW}[2/5] 创建日志目录...${NC}"
mkdir -p logs screenshots
echo -e "${GREEN}✓ 日志目录已创建${NC}"

# 3. 安装 Python 依赖（可选）
echo -e "${YELLOW}[3/5] 准备 Python 环境...${NC}"
if command -v python3 &> /dev/null; then
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Python 环境已配置${NC}"
    else
        echo -e "${GREEN}✓ Python 虚拟环境已存在${NC}"
    fi
fi

# 4. 构建 Docker 镜像（可选）
echo -e "${YELLOW}[4/5] 准备 Docker 环境...${NC}"
if command -v docker &> /dev/null; then
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${YELLOW}   docker-compose.yml 不存在${NC}"
    else
        echo -e "${GREEN}✓ Docker 环境已准备${NC}"
    fi
fi

# 5. 显示启动说明
echo -e "${YELLOW}[5/5] 生成启动说明...${NC}"
echo -e "${GREEN}✓ 所有准备工作已完成${NC}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  启动服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}选择启动方式:${NC}"
echo ""
echo -e "  ${GREEN}1)${NC} Docker Compose (推荐)"
echo -e "     ${BLUE}$ docker-compose up -d${NC}"
echo ""
echo -e "  ${GREEN}2)${NC} 本地 Python"
echo -e "     ${BLUE}$ source venv/bin/activate${NC}"
echo -e "     ${BLUE}$ uvicorn app.main:app --reload${NC}"
echo ""
echo -e "  ${GREEN}3)${NC} 使用 Makefile"
echo -e "     ${BLUE}$ make up${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  验证服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}服务启动后，访问:${NC}"
echo ""
echo -e "  API 文档:    ${GREEN}http://localhost:8000/api/docs${NC}"
echo -e "  Health:      ${GREEN}http://localhost:8000/health${NC}"
echo -e "  Metrics:     ${GREEN}http://localhost:8000/metrics${NC}"
echo -e "  Stats:       ${GREEN}http://localhost:8000/stats${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  需要帮助?${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  📚 查看文档: ${GREEN}cat DEPLOYMENT.md${NC}"
echo -e "  📡 API 文档: ${GREEN}cat API.md${NC}"
echo -e "  🔐 验证码:   ${GREEN}cat CAPTCHA_HANDLING.md${NC}"
echo -e "  📊 监控:     ${GREEN}cat MONITORING.md${NC}"
echo ""

echo -e "${GREEN}✓ 快速开始完成！${NC}"
echo ""