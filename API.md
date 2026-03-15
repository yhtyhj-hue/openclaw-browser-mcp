# 📡 API 文档

## 基础信息

- **基础 URL**: `http://localhost:8000`
- **API 版本**: 1.0.0
- **文档**: http://localhost:8000/api/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/api/redoc

---

## 📋 API 端点总览

### 会话管理 (7个端点)

| 方法 | 端点 | 说明 |
|-----|------|------|
| POST | `/session/open` | 创建新会话 |
| POST | `/session/{id}/close` | 关闭会话 |
| GET | `/session/list` | 列出所有会话 |

### 浏览器操作 (12个端点)

| 方法 | 端点 | 说明 |
|-----|------|------|
| POST | `/session/{id}/navigate` | 导航到 URL |
| POST | `/session/{id}/click` | 点击元素 |
| POST | `/session/{id}/input` | 输入文本 |
| POST | `/session/{id}/scroll` | 滚动页面 |
| GET | `/session/{id}/screenshot` | 获取截图 |
| GET | `/session/{id}/html` | 获取页面 HTML |
| GET | `/session/{id}/text` | 获取页面文本 |
| GET | `/session/{id}/elements` | 获取所有元素 |

### 验证码处理 (2个端点)

| 方法 | 端点 | 说明 |
|-----|------|------|
| POST | `/session/{id}/captcha/detect` | 检测验证码 |
| POST | `/session/{id}/captcha/solve` | 自动解决验证码 |

### 内容提取 (7个端点)

| 方法 | 端点 | 说明 |
|-----|------|------|
| POST | `/session/{id}/content/extract` | 结构化提取内容 |
| GET | `/session/{id}/content/links` | 提取所有链接 |
| GET | `/session/{id}/content/images` | 提取所有图片 |
| GET | `/session/{id}/content/forms` | 提取所有表单 |
| GET | `/session/{id}/content/tables` | 提取所有表格 |

### 交互操作 (8个端点)

| 方法 | 端点 | 说明 |
|-----|------|------|
| POST | `/session/{id}/interaction/fill-form` | 填充表单 |
| POST | `/session/{id}/interaction/multi-click` | 多步点击 |
| POST | `/session/{id}/interaction/wait` | 等待元素 |
| POST | `/session/{id}/interaction/keyboard` | 键盘事件 |
| POST | `/session/{id}/interaction/hover` | 悬停元素 |

### 高级功能 (10个端点)

| 方法 | 端点 | 说明 |
|-----|------|------|
| POST | `/session/{id}/advanced/execute-script` | 执行 JavaScript |
| GET | `/session/{id}/advanced/cookies` | 获取 Cookies |
| POST | `/session/{id}/advanced/cookies/add` | 添加 Cookie |
| GET | `/session/{id}/advanced/storage/local` | 获取本地存储 |
| GET | `/session/{id}/advanced/performance` | 获取性能指标 |

### 工作流 (4个端点)

| 方法 | 端点 | 说明 |
|-----|------|------|
| POST | `/session/{id}/workflow/create` | 创建工作流 |
| GET | `/session/{id}/workflow/list` | 列出工作流 |
| POST | `/session/{id}/workflow/execute` | 执行工作流 |

---

## 📘 详细使用示例

### 1. 创建会话

**请求:**

```bash
curl -X POST http://localhost:8000/session/open \
  -H "Content-Type: application/json"
```

**响应:**

```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "status": "active",
  "created_at": "2026-03-14T10:30:00.000000"
}
```

### 2. 导航到网站

**请求:**

```bash
curl -X POST http://localhost:8000/session/sess_a1b2c3d4e5f6/navigate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com",
    "wait_until": "networkidle"
  }'
```

**响应:**

```json
{
  "status": "success",
  "url": "https://www.example.com",
  "title": "Example Domain",
  "status_code": 200
}
```

### 3. 填充表单并提交

**请求:**

```bash
curl -X POST http://localhost:8000/session/sess_a1b2c3d4e5f6/interaction/fill-form \
  -H "Content-Type: application/json" \
  -d '{
    "fields": [
      {
        "selector": "input[name=username]",
        "value": "user@example.com"
      },
      {
        "selector": "input[name=password]",
        "value": "MyPassword123!"
      }
    ],
    "submit_selector": "button[type=submit]",
    "use_human_behavior": true
  }'
```

**响应:**

```json
{
  "status": "success",
  "fields_filled": 2,
  "results": [
    {"selector": "input[name=username]", "status": "success"},
    {"selector": "input[name=password]", "status": "success"},
    {"selector": "button[type=submit]", "status": "submitted"}
  ]
}
```

### 4. 提取页面内容

**请求:**

```bash
curl -X POST http://localhost:8000/session/sess_a1b2c3d4e5f6/content/extract \
  -H "Content-Type: application/json" \
  -d '{
    "extract_text": true,
    "extract_links": true,
    "extract_forms": true,
    "extract_tables": true,
    "extract_images": false
  }'
```

**响应:**

```json
{
  "status": "success",
  "timestamp": null,
  "text": "Page content here...",
  "links": [
    {
      "text": "Homepage",
      "href": "https://example.com",
      "title": "Home"
    }
  ],
  "forms": [
    {
      "id": "login-form",
      "action": "/login",
      "method": "POST",
      "fields": [...]
    }
  ],
  "tables": [...]
}
```

### 5. 自动解决验证码

**请求:**

```bash
curl -X POST http://localhost:8000/session/sess_a1b2c3d4e5f6/captcha/solve \
  -H "Content-Type: application/json" \
  -d '{
    "auto_retry": true,
    "max_attempts": 3,
    "timeout": 60
  }'
```

**响应:**

```json
{
  "status": "success",
  "captcha_type": "slider",
  "solved": true,
  "attempts": 1
}
```

### 6. 执行工作流

**创建工作流:**

```bash
curl -X POST http://localhost:8000/session/sess_a1b2c3d4e5f6/workflow/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Login Workflow",
    "description": "自动登录流程",
    "steps": [
      {
        "action": "navigate",
        "value": "https://example.com/login"
      },
      {
        "action": "input",
        "selector": "input[name=username]",
        "value": "user@example.com",
        "wait_time": 1
      },
      {
        "action": "input",
        "selector": "input[name=password]",
        "value": "password123"
      },
      {
        "action": "click",
        "selector": "button[type=submit]",
        "wait_time": 2
      },
      {
        "action": "wait",
        "selector": ".dashboard",
        "timeout": 5000
      }
    ]
  }'
```

**响应:**

```json
{
  "status": "success",
  "workflow_id": "wf_1a2b3c4d5e6f",
  "name": "Login Workflow"
}
```

**执行工作流:**

```bash
curl -X POST http://localhost:8000/session/sess_a1b2c3d4e5f6/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf_1a2b3c4d5e6f",
    "session_id": "sess_a1b2c3d4e5f6"
  }'
```

---

## 📊 常见错误代码

| 代码 | 说明 | 解决方案 |
|------|------|---------|
| 400 | 请求参数错误 | 检查请求体格式 |
| 404 | 会话/资源不存在 | 检查 session_id 是否正确 |
| 408 | 操作超时 | 增加 timeout 值 |
| 422 | 验证错误 | 检查请求参数类型 |
| 500 | 服务器错误 | 查看服务器日志 |

---

## 🔒 认证 (可选)

如果启用了 API 密钥认证:

```bash
curl -X POST http://localhost:8000/session/open \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 📈 性能优化建议

1. **重用会话** - 不要频繁创建/销毁会话
2. **批量操作** - 使用工作流而不是逐个调用 API
3. **合理设置超时** - 根据网络状况调整
4. **启用缓存** - 对重复请求使用缓存

---

## 🧪 测试 API

### 使用 curl

```bash
# 完整的登录测试流程
SESSION=$(curl -s -X POST http://localhost:8000/session/open | jq -r '.session_id')
echo "会话 ID: $SESSION"

# 导航
curl -X POST http://localhost:8000/session/$SESSION/navigate \
  -d '{"url": "https://example.com"}'

# 获取截图
curl -X GET http://localhost:8000/session/$SESSION/screenshot > screenshot.png

# 关闭会话
curl -X POST http://localhost:8000/session/$SESSION/close
```

### 使用 Python

```python
import requests

# 创建会话
resp = requests.post('http://localhost:8000/session/open')
session_id = resp.json()['session_id']

# 导航
requests.post(
    f'http://localhost:8000/session/{session_id}/navigate',
    json={'url': 'https://example.com'}
)

# 填充表单
requests.post(
    f'http://localhost:8000/session/{session_id}/interaction/fill-form',
    json={
        'fields': [
            {'selector': 'input[name=q]', 'value': 'python'}
        ]
    }
)

# 获取截图
resp = requests.get(f'http://localhost:8000/session/{session_id}/screenshot')
with open('screenshot.png', 'wb') as f:
    f.write(resp.content)

# 关闭会话
requests.post(f'http://localhost:8000/session/{session_id}/close')
```

### 使用 JavaScript

```javascript
// 创建会话
const openResp = await fetch('http://localhost:8000/session/open', {
  method: 'POST'
});
const { session_id } = await openResp.json();

// 导航
await fetch(`http://localhost:8000/session/${session_id}/navigate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com' })
});

// 填充表单
await fetch(`http://localhost:8000/session/${session_id}/interaction/fill-form`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fields: [{ selector: 'input[name=q]', value: 'python' }]
  })
});

// 获取截图
const screenshot = await fetch(
  `http://localhost:8000/session/${session_id}/screenshot`
);
const blob = await screenshot.blob();
```

---

更多信息查看: [API Docs](http://localhost:8000/api/docs)