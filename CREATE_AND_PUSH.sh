#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_step() {
    echo -e "${YELLOW}[$1] $2${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# 主程序开始
clear
print_header "OpenClaw Browser MCP Server - 一键发布脚本"

# ==================== 第 1 步：检查前置条件 ====================
print_step "1/8" "检查前置条件"

if ! command -v git &> /dev/null; then
    print_error "Git 未安装"
    exit 1
fi
print_success "Git 已安装"

if ! command -v curl &> /dev/null; then
    print_error "curl 未安装"
    exit 1
fi
print_success "curl 已安装"

echo ""

# ==================== 第 2 步：获取 GitHub 信息 ====================
print_step "2/8" "获取 GitHub 信息"

echo ""
read -p "请输入 GitHub 用户名 [yhtyhj-hue]: " GITHUB_USER
GITHUB_USER=${GITHUB_USER:-yhtyhj-hue}
print_success "GitHub 用户名: $GITHUB_USER"

read -p "请输入 GitHub 个人访问令牌 (PAT): " GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    print_error "GitHub token 为空"
    exit 1
fi
print_success "GitHub token 已设置"

REPO_NAME="openclaw-browser-mcp"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo ""

# ==================== 第 3 步：验证 GitHub 凭证 ====================
print_step "3/8" "验证 GitHub 凭证"

RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/user)

if echo "$RESPONSE" | grep -q "\"login\""; then
    GITHUB_LOGIN=$(echo "$RESPONSE" | grep -o '"login": "[^"]*' | cut -d'"' -f4)
    print_success "认证成功: $GITHUB_LOGIN"
else
    print_error "GitHub token 无效，请检查输入"
    exit 1
fi

echo ""

# ==================== 第 4 步：检查仓库是否存在 ====================
print_step "4/8" "检查仓库是否存在"

REPO_CHECK=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME")

if echo "$REPO_CHECK" | grep -q "\"id\""; then
    print_info "仓库已存在，将进行更新"
else
    print_step "4/8" "创建新仓库"
    
    CREATE_RESPONSE=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d '{
            "name": "'$REPO_NAME'",
            "description": "为 OpenClaw AI 提供浏览器自动化、页面理解、验证码识别的 MCP 服务",
            "homepage": "",
            "private": false,
            "has_issues": true,
            "has_projects": true,
            "has_downloads": true,
            "has_wiki": true,
            "auto_init": false
        }')
    
    if echo "$CREATE_RESPONSE" | grep -q "\"id\""; then
        print_success "仓库已创建"
    else
        print_error "创建仓库失败"
        echo "$CREATE_RESPONSE"
        exit 1
    fi
fi

echo ""

# ==================== 第 5 步：配置本地 Git ====================
print_step "5/8" "配置本地 Git 仓库"

# 检查是否已初始化
if [ ! -d ".git" ]; then
    git init
    print_success "Git 仓库已初始化"
else
    print_success "Git 仓库已存在"
fi

# 配置用户信息
if [ -z "$(git config user.name)" ]; then
    read -p "请输入 Git 用户名: " GIT_NAME
    git config user.name "$GIT_NAME"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "请输入 Git 邮箱: " GIT_EMAIL
    git config user.email "$GIT_EMAIL"
fi

GIT_NAME=$(git config user.name)
GIT_EMAIL=$(git config user.email)
print_success "Git 用户: $GIT_NAME <$GIT_EMAIL>"

echo ""

# ==================== 第 6 步：添加文件到 Git ====================
print_step "6/8" "添加文件到 Git"

git add .
FILES_COUNT=$(git diff --cached --name-only | wc -l)
print_success "已添加 $FILES_COUNT 个文件"

echo ""

# ==================== 第 7 步：创建提交 ====================
print_step "7/8" "创建初始提交"

COMMIT_MESSAGE="feat: 初始化 OpenClaw Browser MCP Server 项目

✨ 核心功能:
  - Playwright 浏览器自动化框架
  - 支持多种验证码处理 (图片、滑块、reCAPTCHA 等)
  - 真人级别行为模拟 (鼠标、键盘、延迟)
  - 完整的 RESTful API 接口 (43+ 端点)
  - 异步并发处理
  - 完整的监控和日志系统
  - Docker 容器化部署
  - Prometheus + Grafana 集成
  - ELK Stack 日志管理

📦 项目结构:
  - app/                应用核心代码 (8 个模块)
  - docs/               完整文档
  - tests/              单元测试
  - docker-compose*     Docker 编排配置
  - requirements.txt    Python 依赖

🚀 快速开始:
  docker-compose up -d

📚 文档:
  - DEPLOYMENT.md      详���部署指南
  - API.md            完整 API 文档
  - CAPTCHA_HANDLING.md 验证码处理指南
  - MONITORING.md     监控系统指南

🔧 技术栈:
  - Python 3.11+
  - FastAPI
  - Playwright
  - Prometheus
  - Docker & Nginx

✅ 已包含:
  - 全面的错误处理
  - 详细的日志系统
  - 性能监控
  - 健康检查
  - 告警系统
  - 完整的部署文档"

if git commit -m "$COMMIT_MESSAGE"; then
    print_success "初始提交已创建"
else
    print_error "提交失败"
    exit 1
fi

echo ""

# ==================== 第 8 步：推送到 GitHub ====================
print_step "8/8" "推送到 GitHub"

# 移除旧的远程配置（如果存在）
git remote remove origin 2>/dev/null

# 添加新的远程配置（使用 token 认证）
REMOTE_WITH_TOKEN="https://$GITHUB_USER:$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"
git remote add origin "$REMOTE_WITH_TOKEN"

# 重命名分支为 main（如需要）
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    print_success "主分支已重命名为 main"
fi

# 推送到 GitHub
if git push -u origin main; then
    print_success "代码已成功推送到 GitHub"
else
    print_error "推送失败，请检查网络连接"
    exit 1
fi

# 移除 token 从远程 URL（安全起见）
git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo ""
print_header "✓ 发布完成！"

echo ""
echo -e "${GREEN}仓库信息:${NC}"
echo -e "  地址: ${CYAN}https://github.com/$GITHUB_USER/$REPO_NAME${NC}"
echo ""

echo -e "${GREEN}后续步骤:${NC}"
echo -e "  1. 访问仓库: ${CYAN}https://github.com/$GITHUB_USER/$REPO_NAME${NC}"
echo -e "  2. 配置仓库设置 (Settings)"
echo -e "  3. 添加主题标签"
echo -e "  4. 启用 Discussions"
echo -e "  5. 配置 Branch Protection"
echo ""

echo -e "${GREEN}查看提交:${NC}"
git log --oneline -1

echo ""
print_success "所有操作已完成！"