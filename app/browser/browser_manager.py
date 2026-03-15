import asyncio
import uuid
from typing import Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)

class BrowserSession:
    """浏览器会话封装"""
    
    def __init__(self, session_id: str, browser: Browser):
        self.session_id = session_id
        self.browser = browser
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.created_at = None
        self.last_activity = None
    
    async def initialize(self):
        """初始化会话"""
        try:
            self.context = await self.browser.new_context(
                user_agent=settings.user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True,
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(settings.browser_timeout)
            self.page.set_default_navigation_timeout(settings.browser_timeout)
            self.created_at = asyncio.get_event_loop().time()
            self.last_activity = self.created_at
            logger.info(f"Session {self.session_id} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize session {self.session_id}: {e}")
            raise
    
    async def close(self):
        """关闭会话"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            logger.info(f"Session {self.session_id} closed")
        except Exception as e:
            logger.error(f"Error closing session {self.session_id}: {e}")
    
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = asyncio.get_event_loop().time()

class BrowserManager:
    """浏览器管理器 - 管理多个浏览器会话"""
    
    def __init__(self, max_sessions: int = 10):
        self.max_sessions = max_sessions
        self.sessions: Dict[str, BrowserSession] = {}
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """初始化浏览器管理器"""
        try:
            self.playwright = await async_playwright().start()
            
            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-sync",
                "--disable-web-resources",
                "--disable-extensions",
            ]
            
            if settings.disable_automation:
                args.append("--start-maximized")
            
            self.browser = await self.playwright.chromium.launch(
                headless=settings.headless,
                args=args,
                slow_mo=50,  # 50ms 延迟 - 模拟真人操作
            )
            logger.info("Browser manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser manager: {e}")
            raise
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """创建新会话"""
        async with self.lock:
            if len(self.sessions) >= self.max_sessions:
                raise Exception(f"Max sessions ({self.max_sessions}) reached")
            
            session_id = f"sess_{uuid.uuid4().hex[:12]}"
            
            try:
                session = BrowserSession(session_id, self.browser)
                await session.initialize()
                self.sessions[session_id] = session
                logger.info(f"New session created: {session_id} (user: {user_id})")
                return session_id
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                raise
    
    async def get_session(self, session_id: str) -> BrowserSession:
        """获取会话"""
        if session_id not in self.sessions:
            raise Exception(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session.update_activity()
        return session
    
    async def close_session(self, session_id: str):
        """关闭会话"""
        async with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                await session.close()
                del self.sessions[session_id]
                logger.info(f"Session {session_id} closed and removed")
    
    async def cleanup(self):
        """清理所有资源"""
        async with self.lock:
            for session_id in list(self.sessions.keys()):
                await self.close_session(session_id)
            
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser manager cleaned up")
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数"""
        return len(self.sessions)
    
    def get_sessions_info(self) -> Dict:
        """获取所有会话信息"""
        return {
            session_id: {
                "created_at": session.created_at,
                "last_activity": session.last_activity,
            }
            for session_id, session in self.sessions.items()
        }