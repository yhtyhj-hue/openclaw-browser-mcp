#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OpenClaw Browser MCP Server${NC}"
echo -e "${BLUE}  GitHub 一键提交脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git 已安装${NC}"
echo ""

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}[1/7] 初始化 Git 仓库...${NC}"
    git init
    echo -e "${GREEN}✓ Git 仓库已初始化${NC}"
else
    echo -e "${GREEN}✓ Git 仓库已存在${NC}"
fi

echo ""
echo -e "${YELLOW}[2/7] 配置 Git 用户信息...${NC}"

# 检查并配置 Git 用户信息
if git config --global user.name > /dev/null; then
    echo -e "${GREEN}✓ Git 用户已配置${NC}"
else
    echo -e "${YELLOW}   请输入你的名字:${NC}"
    read -p "   名字: " git_name
    git config --global user.name "$git_name"
    echo ""
    echo -e "${YELLOW}   请输入你的邮箱:${NC}"
    read -p "   邮箱: " git_email
    git config --global user.email "$git_email"
    echo -e "${GREEN}✓ Git 用户信息已配置${NC}"
fi

echo ""
echo -e "${YELLOW}[3/7] 添加所有文件...${NC}"
git add .
echo -e "${GREEN}✓ 所有文件已添加${NC}"

echo ""
echo -e "${YELLOW}[4/7] 检查改动${NC}"
git status

echo ""
echo -e "${YELLOW}[5/7] 创建初始提交...${NC}"
if git commit -m "feat: 初始化 OpenClaw Browser MCP Server 项目

✨ 功能特性:
  - 完整的浏览器自动化框架 (Playwright)
  - 支持多种验证码处理 (图片、滑块、reCAPTCHA 等)
  - 真人级别行为模拟 (鼠标、键盘、延迟)
  - 完整的 RESTful API 接口
  - 异步并发处理支持
  - 完整的监控和日志系统
  - Docker 容器化部署
  - Prometheus + Grafana 集成
  - ELK Stack 日志管理
  - 详细的部署和使用文档

📦 项目结构:
  - app/               应用核心代码
  - docs/              文档
  - tests/             单元测试
  - docker-compose*    Docker 配置
  - requirements.txt   Python 依赖

🚀 快速开始:
  docker-compose up -d

📚 文档:
  - DEPLOYMENT.md      部署指南
  - API.md            API 文档
  - CAPTCHA_HANDLING.md 验证码处理
  - MONITORING.md     监控指南"; then
    echo -e "${GREEN}✓ 初始提交已创建${NC}"
else
    echo -e "${YELLOW}✓ 没有新改动或已提交${NC}"
fi

echo ""
echo -e "${YELLOW}[6/7] 配置远程仓库...${NC}"

# 检查是否已配置远程仓库
if git remote | grep -q "^origin$"; then
    REMOTE_URL=$(git remote get-url origin)
    echo -e "${GREEN}✓ 远程仓库已配置: $REMOTE_URL${NC}"
else
    echo -e "${YELLOW}   请输入 GitHub 仓库 URL:${NC}"
    read -p "   URL: " remote_url
    git remote add origin "$remote_url"
    echo -e "${GREEN}✓ 远程仓库已配置${NC}"
fi

echo ""
echo -e "${YELLOW}[7/7] 推送到 GitHub...${NC}"

# 检查并重命名主分支
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    echo -e "${GREEN}✓ 主分支已重命名为 main${NC}"
fi

# 推送到 GitHub
if git push -u origin main; then
    echo -e "${GREEN}✓ 代码已推送到 GitHub${NC}"
else
    echo -e "${YELLOW}⚠️  推送失败，请检查网络和 GitHub 访问权限${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ✓ 全部完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 显示仓库信息
REPO_URL=$(git remote get-url origin)
echo -e "${GREEN}仓库地址:${NC}"
echo -e "  ${BLUE}$REPO_URL${NC}"
echo ""
echo -e "${GREEN}访问地址:${NC}"
echo -e "  ${BLUE}$(echo $REPO_URL | sed 's/\.git$//')${NC}"
echo ""

echo -e "${GREEN}后续操作:${NC}"
echo -e "  1. 访问仓库: $REPO_URL"
echo -e "  2. 添加说明文档"
echo -e "  3. 配置 GitHub Pages"
echo -e "  4. 设置 CI/CD"
echo ""

git log --oneline -1
echo ""