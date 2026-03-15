# 📦 安装指南

## 快速安装

### 方式 1: Docker Compose (推荐)

```bash
# 只需 3 条命令！
git clone https://github.com/yhtyhj-hue/openclaw-browser-mcp.git
cd openclaw-browser-mcp
docker-compose up -d
```

然后访问 http://localhost:8000 ✨

### 方式 2: 本地 Python

```bash
git clone https://github.com/yhtyhj-hue/openclaw-browser-mcp.git
cd openclaw-browser-mcp

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
playwright install

# 运行
uvicorn app.main:app --reload
```

---

## 系统要求

| 组件 | 要求 |
|------|------|
| 操作系统 | Linux / macOS / Windows (WSL2) |
| Python | 3.11+ (本地运行时) |
| Docker | 20.10+ (Docker 方式) |
| 内存 | 4GB+ |
| 磁盘 | 5GB+ (用于浏览器) |
| 网络 | 稳定的互联网连接 |

---

## 详细步骤

### 第 1 步: 克隆仓库

```bash
git clone https://github.com/yhtyhj-hue/openclaw-browser-mcp.git
cd openclaw-browser-mcp
```

### 第 2 步: 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件（可选）
nano .env
```

### 第 3 步: 选择运行方式

#### 选项 A: Docker Compose

```bash
# 启动
docker-compose up -d

# 验证
curl http://localhost:8000/health

# 查看日志
docker-compose logs -f
```

#### 选项 B: 本地 Python

```bash
# 安装依赖
pip install -r requirements.txt

# 安装浏览器
playwright install chromium

# 运行
python -m app.main
```

#### 选项 C: 使用 Makefile

```bash
# 查看可用命令
make help

# 构建镜像
make build

# 启动服务
make up

# 查看日志
make logs
```

### 第 4 步: 验证安装

```bash
# 检查服务状态
curl http://localhost:8000/health

# 查看 API 文档
# 浏览器访问: http://localhost:8000/api/docs

# 创建测试会话
curl -X POST http://localhost:8000/session/open
```

---

## 故障排除

### 问题: 浏览器启动失败

**解决方案:**

```bash
# 重新安装 Playwright
playwright install --with-deps

# 或手动安装系统依赖
# Ubuntu/Debian:
sudo apt-get install -y libwdl-core1 libx11-6 libxcb1

# macOS:
brew install chromium
```

### 问题: 端口被占用

**解决方案:**

```bash
# 检查占用端口的进程
lsof -i :8000

# 更改端口 (.env)
SERVER_PORT=8001

# 或杀死占用进程
kill -9 <PID>
```

### 问题: 权限拒绝错误

**解决方案:**

```bash
# 修复 Docker 权限
sudo usermod -aG docker $USER
newgrp docker

# 或使用 sudo
sudo docker-compose up -d
```

### 问题: 磁盘空间不足

**解决方案:**

```bash
# 清理 Docker 资源
docker system prune -a

# 或检查磁盘使用
df -h
du -sh docker/
```

---

## 下一步

安装完成后：

1. ✅ 查看 [API 文档](./API.md)
2. ✅ 查看 [部署指南](./DEPLOYMENT.md)
3. ✅ 查看 [验证码处理](./CAPTCHA_HANDLING.md)

祝你使用愉快！