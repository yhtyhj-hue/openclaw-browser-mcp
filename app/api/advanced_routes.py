from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
from app.main import browser_manager
from app.browser.browser_actions import BrowserActions
from app.browser.human_behavior import HumanBehavior
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class ScriptExecuteRequest(BaseModel):
    """执行JavaScript脚本"""
    script: str
    args: Optional[list] = None

class CookieRequest(BaseModel):
    """Cookie操作"""
    name: str
    value: str
    domain: Optional[str] = None
    path: str = "/"

class LocalStorageRequest(BaseModel):
    """本地存储操作"""
    key: str
    value: str

class ScreenRecordRequest(BaseModel):
    """屏幕录制"""
    duration: float = 10.0  # 秒
    format: str = "mp4"

@router.post("/{session_id}/advanced/execute-script")
async def execute_javascript(session_id: str, req: ScriptExecuteRequest = Body(...)):
    """
    执行JavaScript代码
    
    示例:
    {
        "script": "return document.title",
        "args": []
    }
    """
    try:
        session = await browser_manager.get_session(session_id)
        
        result = await session.page.evaluate(req.script, req.args)
        
        logger.info(f"JavaScript executed in session {session_id}")
        return {
            "status": "success",
            "result": result,
        }
        
    except Exception as e:
        logger.error(f"JavaScript execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/advanced/cookies")
async def get_cookies(session_id: str):
    """获取所有Cookies"""
    try:
        session = await browser_manager.get_session(session_id)
        cookies = await session.context.cookies()
        
        return {
            "count": len(cookies),
            "cookies": cookies,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/advanced/cookies/add")
async def add_cookie(session_id: str, req: CookieRequest = Body(...)):
    """添加Cookie"""
    try:
        session = await browser_manager.get_session(session_id)
        
        cookie = {
            "name": req.name,
            "value": req.value,
            "domain": req.domain or session.page.url.split("/")[2],
            "path": req.path,
        }
        
        await session.context.add_cookies([cookie])
        
        logger.info(f"Cookie added: {req.name}")
        return {
            "status": "success",
            "cookie": cookie,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/advanced/cookies/clear")
async def clear_cookies(session_id: str):
    """清除所有Cookies"""
    try:
        session = await browser_manager.get_session(session_id)
        await session.context.clear_cookies()
        
        logger.info("Cookies cleared")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/advanced/storage/local")
async def get_local_storage(session_id: str):
    """获取本地存储"""
    try:
        session = await browser_manager.get_session(session_id)
        
        storage = await session.page.evaluate("() => window.localStorage")
        
        return {
            "count": len(storage),
            "storage": storage,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/advanced/storage/local/set")
async def set_local_storage(session_id: str, req: LocalStorageRequest = Body(...)):
    """设置本地存储"""
    try:
        session = await browser_manager.get_session(session_id)
        
        await session.page.evaluate(
            f"() => window.localStorage.setItem('{req.key}', '{req.value}')"
        )
        
        logger.info(f"LocalStorage set: {req.key}")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/advanced/performance")
async def get_performance_metrics(session_id: str):
    """获取页面性能指标"""
    try:
        session = await browser_manager.get_session(session_id)
        
        metrics = await session.page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    dns: navigation.domainLookupEnd - navigation.domainLookupStart,
                    tcp: navigation.connectEnd - navigation.connectStart,
                    ttfb: navigation.responseStart - navigation.requestStart,
                    download: navigation.responseEnd - navigation.responseStart,
                    dom_interactive: navigation.domInteractive - navigation.fetchStart,
                    dom_complete: navigation.domComplete - navigation.fetchStart,
                    load_complete: navigation.loadEventEnd - navigation.fetchStart,
                };
            }
        """)
        
        return {
            "status": "success",
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/advanced/network/intercept")
async def intercept_requests(session_id: str, pattern: str = Body(...)):
    """
    拦截网络请求
    
    示例: pattern = "*.api.*" 或 "**.json"
    """
    try:
        session = await browser_manager.get_session(session_id)
        
        intercepted_requests = []
        
        async def handle_route(route):
            intercepted_requests.append({
                "url": route.request.url,
                "method": route.request.method,
                "headers": dict(route.request.headers),
            })
            await route.continue_()
        
        await session.page.route(pattern, handle_route)
        
        logger.info(f"Network interception started for pattern: {pattern}")
        return {
            "status": "success",
            "pattern": pattern,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/advanced/dialog/handle")
async def handle_dialog(session_id: str, action: str = Body(...)):
    """
    处理弹窗 (alert, confirm, prompt)
    
    action: "accept" 或 "dismiss"
    """
    try:
        session = await browser_manager.get_session(session_id)
        
        async def dialog_handler(dialog):
            if action == "accept":
                await dialog.accept()
            else:
                await dialog.dismiss()
        
        session.page.once("dialog", dialog_handler)
        
        logger.info(f"Dialog handler set to {action}")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/advanced/viewport/set")
async def set_viewport(session_id: str, width: int, height: int):
    """设置视口大小"""
    try:
        session = await browser_manager.get_session(session_id)
        await session.page.set_viewport_size({"width": width, "height": height})
        
        logger.info(f"Viewport set to {width}x{height}")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/advanced/page-info")
async def get_full_page_info(session_id: str):
    """获取完整的页面信息"""
    try:
        session = await browser_manager.get_session(session_id)
        
        info = await session.page.evaluate("""
            () => {
                return {
                    url: window.location.href,
                    title: document.title,
                    referrer: document.referrer,
                    cookies: document.cookie,
                    encoding: document.characterSet,
                    language: navigator.language,
                    user_agent: navigator.userAgent,
                    screen_width: window.screen.width,
                    screen_height: window.screen.height,
                    viewport_width: window.innerWidth,
                    viewport_height: window.innerHeight,
                };
            }
        """)
        
        return {
            "status": "success",
            "info": info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/advanced/file/upload")
async def upload_file(session_id: str, selector: str, file_path: str = Body(...)):
    """上传文件"""
    try:
        session = await browser_manager.get_session(session_id)
        
        input_element = await session.page.query_selector(selector)
        if not input_element:
            raise Exception(f"File input not found: {selector}")
        
        await input_element.set_input_files(file_path)
        
        logger.info(f"File uploaded: {file_path}")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))