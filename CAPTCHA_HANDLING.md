# 🔐 验证码处理完整指南

## 支持的验证码类型

| 类型 | 支持 | 方法 | 难度 |
|------|------|------|------|
| 图片验���码 | ✅ | OCR + 打码平台 | 简单 |
| 滑块验证码 | ✅ | 轨迹还原 | 中等 |
| 点选验证码 | ✅ | 图像识别 | 中等 |
| reCAPTCHA v2 | ✅ | 2Captcha/AntiCaptcha | 困难 |
| reCAPTCHA v3 | ⚠️ | 需特殊处理 | 很困难 |
| hCAPTCHA | ✅ | 2Captcha/AntiCaptcha | 困难 |
| 短信验证码 | ⚠️ | 手动/第三方短信服务 | 困难 |

---

## 1. 图片验证码

### 原理

自动截图验证码 → 使用 OCR 识别 → 填充答案

### 配置

在 `.env` 中:

```env
CAPTCHA_PROVIDER=ocr
```

### 使用示例

```bash
curl -X POST http://localhost:8000/session/sess_xxx/captcha/solve \
  -H "Content-Type: application/json" \
  -d '{
    "auto_retry": true,
    "max_attempts": 3
  }'
```

### 响应

```json
{
  "status": "success",
  "captcha_type": "image",
  "solved": true,
  "attempts": 1
}
```

---

## 2. 滑块验证码

### 原理

1. 检测滑块
2. 计算滑动距离
3. 生成人类级别的轨迹
4. 模拟拖拽

### 配置

```env
CAPTCHA_PROVIDER=slider
SLIDER_TIMEOUT=30
```

### 工作原理代码

```python
# 生成贝塞尔曲线轨迹
trajectory = SliderSolver.generate_slider_trajectory(
    distance=280,        # 需要滑动的距离
    duration=2.0,        # 总耗时2秒
    overshoot=True       # 先超过再返回（更真实）
)

# 执行拖拽
for x_offset, delay in trajectory:
    mouse.move(x_offset)
    sleep(delay)
```

### 自动解决

```bash
curl -X POST http://localhost:8000/session/sess_xxx/captcha/solve
```

---

## 3. reCAPTCHA v2

### 原理

通过打码平台的浏览器自动化能力解决

### 配置

在 `.env` 中:

```env
CAPTCHA_PROVIDER=2captcha
CAPTCHA_API_KEY=your_2captcha_api_key
```

### 获取 API 密钥

1. 访问 [2Captcha.com](https://2captcha.com)
2. 注册账户
3. 复制 API Key
4. 添加到 `.env`

### 使用

```bash
curl -X POST http://localhost:8000/session/sess_xxx/captcha/solve \
  -H "Content-Type: application/json" \
  -d '{
    "captcha_type": "recaptcha",
    "auto_retry": true
  }'
```

---

## 4. 打码平台集成

### 4.1 2Captcha

#### 优点
- 支持众多验证码类型
- API 简单易用
- 价格便宜 ($0.30-0.50 / 1000)

#### 配置

```env
CAPTCHA_PROVIDER=2captcha
CAPTCHA_API_KEY=xxxxxxxxxxxx
TWOCAPTCHA_API_URL=http://2captcha.com
```

#### 完整配置示例

```python
# app/config.py
class Settings(BaseSettings):
    captcha_provider: str = "2captcha"
    captcha_api_key: str = ""
    twocaptcha_url: str = "http://2captcha.com"
    twocaptcha_timeout: int = 180  # 秒
```

#### 使用代码

```python
from app.captcha.solver_2captcha import TwoCaptchaSolver

# 解决图片验证码
result = await TwoCaptchaSolver.solve_image(
    image_path="captcha.png",
    api_key="your_key"
)

# 解决 reCAPTCHA
result = await TwoCaptchaSolver.solve_recaptcha(
    site_key="6Le-wvkSAAAAA...",
    page_url="https://example.com",
    api_key="your_key"
)
```

### 4.2 AntiCaptcha

#### 优点
- 支持高级验证码
- 可靠性高
- 支持代理

#### 配置

```env
CAPTCHA_PROVIDER=anticaptcha
CAPTCHA_API_KEY=your_anticaptcha_key
```

#### 使用代码

```python
from app.captcha.solver_anticaptcha import AntiCaptchaSolver

result = await AntiCaptchaSolver.solve(
    task_type="ImageToTextTask",
    image_data=base64_image,
    api_key="your_key"
)
```

---

## 5. 高级配置

### 自动重试机制

```python
# 配置重试
{
    "auto_retry": true,          # 自动重试
    "max_attempts": 3,           # 最多尝试3次
    "timeout": 60,               # 超时60秒
    "fallback_provider": "manual" # 失败时切换到手动
}
```

### 多提供者配置

```python
# 创建 app/config.py
CAPTCHA_PROVIDERS = {
    "primary": {
        "type": "2captcha",
        "api_key": "key1"
    },
    "fallback": {
        "type": "anticaptcha",
        "api_key": "key2"
    }
}
```

### 缓存验证码结果

```python
# 在 Redis 中缓存结果
redis.set(
    f"captcha:{page_url}",
    captcha_result,
    ex=3600  # 1小时过期
)
```

---

## 6. 测试验证码处理

### 测试脚本

```python
import asyncio
from app.captcha.detector import CaptchaDetector
from app.browser.browser_manager import BrowserManager

async def test_captcha_detection():
    # 初始化浏览器
    browser_manager = BrowserManager()
    await browser_manager.initialize()
    
    # 创建会话
    session_id = await browser_manager.create_session()
    session = await browser_manager.get_session(session_id)
    
    # 导航到有验证码的页面
    await session.page.goto("https://example-with-captcha.com")
    
    # 检测验证码
    captcha = await CaptchaDetector.detect(session.page)
    print(f"Detected CAPTCHA: {captcha}")
    
    # 解决验证码
    if captcha:
        result = await solve_captcha(session.page, captcha)
        print(f"Result: {result}")
    
    # 清理
    await browser_manager.close_session(session_id)
    await browser_manager.cleanup()

asyncio.run(test_captcha_detection())
```

### 使用 API 测试

```bash
# 测试检测
curl -X POST http://localhost:8000/session/sess_xxx/captcha/detect

# 测试解决
curl -X POST http://localhost:8000/session/sess_xxx/captcha/solve \
  -H "Content-Type: application/json" \
  -d '{
    "auto_retry": true,
    "max_attempts": 3
  }'
```

---

## 7. 常见问题

### Q: OCR 识别准确率低

**A:** 调整图片预处理参数

```python
# app/captcha/solver_ocr.py
def _preprocess_image(image):
    # 增强对比度
    clahe = cv2.createCLAHE(clipLimit=3.0)  # 增加值
    enhanced = clahe.apply(gray)
    
    # 自���义阈值
    _, binary = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY)
    
    return binary
```

### Q: 滑块识别失败

**A:** 检查滑块选择器

```bash
# 在浏览器 DevTools 中找到滑块
document.querySelectorAll('[class*="slider"]')
document.querySelectorAll('.geetest_slider')

# 更新配置
SLIDER_SELECTOR=".your-slider-class"
```

### Q: 打码平台返回错误

**A:** 检查余额和 API 密钥

```bash
# 检查 2Captcha 余额
curl "http://2captcha.com/api/user?apikey=YOUR_KEY&action=getbalance"

# 余额应该 > 0
# 返回格式: OK|123.45
```

### Q: 验证码解决很慢

**A:** 优化超时设置

```env
# 减少超时时间
CAPTCHA_TIMEOUT=30

# 增加重试次数
CAPTCHA_MAX_RETRIES=1
```

---

## 8. 最佳实践

### ✅ 建议做法

1. **使用打码平台** 处理高级验证码
2. **启用缓存** 避免重复识别
3. **设置合理的超时** 平衡速度和准确性
4. **记录失败日志** 便于调试
5. **定期更新** 配置参数

### ❌ 避免做法

1. ❌ 不要绕过 Captcha（违法）
2. ❌ 不要使用过期的打码 API
3. ❌ 不要在代码中硬编码 API 密钥
4. ❌ 不要忽视验证码错误
5. ❌ 不要过度重试导致成本高

---

## 9. 成本估算

### 打码成本

| 提供商 | 图片验证码 | reCAPTCHA | 滑块 | 点选 |
|--------|----------|----------|------|------|
| 2Captcha | $0.30 | $0.50 | $0.30 | $0.30 |
| AntiCaptcha | $0.50 | $0.50 | $0.50 | $0.50 |

### 成本优化

```python
# 使用本地 OCR 先尝试
if is_simple_captcha:
    result = ocr.recognize(image)
else:
    # 复杂验证码才用付费服务
    result = twocaptcha.solve(image)
```

---

## 参考资源

- [2Captcha 文档](https://2captcha.com/api)
- [AntiCaptcha 文档](https://anti-captcha.com/apidoc)
- [Playwright 文档](https://playwright.dev)
- [OpenCV 文档](https://docs.opencv.org)

---

## 支持

有问题？
- 📧 Email: support@example.com
- 💬 GitHub Issues: https://github.com/yhtyhj-hue/openclaw-browser-mcp/issues
- 📚 Wiki: https://github.com/yhtyhj-hue/openclaw-browser-mcp/wiki