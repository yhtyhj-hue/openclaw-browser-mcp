from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
import io
from pydantic import BaseModel
from typing import Optional
from app.main import browser_manager
from app.browser.browser_actions import BrowserActions
from app.browser.human_behavior import HumanBehavior
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class NavigateRequest(BaseModel):
    url: str
    wait_until: str = "networkidle"

class ClickRequest(BaseModel):
    selector: str
    use_human_behavior: bool = True

class InputRequest(BaseModel):
    selector: str
    text: str
    use_human_behavior: bool = True

@router.post("/{session_id}/navigate")
async def navigate(session_id: str, req: NavigateRequest):
    """导航到 URL"""
    try:
        session = await browser_manager.get_session(session_id)
        result = await BrowserActions.navigate(session.page, req.url, req.wait_until)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/click")
async def click(session_id: str, req: ClickRequest):
    """点击元素"""
    try:
        session = await browser_manager.get_session(session_id)
        result = await BrowserActions.click(session.page, req.selector, req.use_human_behavior)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/input")
async def input_text(session_id: str, req: InputRequest):
    """输入文本"""
    try:
        session = await browser_manager.get_session(session_id)
        result = await BrowserActions.input_text(session.page, req.selector, req.text, req.use_human_behavior)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/screenshot")
async def screenshot(session_id: str, full_page: bool = True):
    """获取截图"""
    try:
        session = await browser_manager.get_session(session_id)
        screenshot_bytes = await BrowserActions.get_screenshot(session.page, full_page)
        return StreamingResponse(io.BytesIO(screenshot_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/html")
async def get_html(session_id: str):
    """获取页面 HTML"""
    try:
        session = await browser_manager.get_session(session_id)
        html = await BrowserActions.get_html(session.page)
        return {"html": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/text")
async def get_text(session_id: str):
    """获取页面文本"""
    try:
        session = await browser_manager.get_session(session_id)
        text = await BrowserActions.get_text(session.page)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/elements")
async def get_elements(session_id: str):
    """获取页面中的交互元素"""
    try:
        session = await browser_manager.get_session(session_id)
        elements = await BrowserActions.get_elements(session.page)
        return {"elements": elements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/scroll")
async def scroll(session_id: str, direction: str = "down", amount: int = 500):
    """滚动页面"""
    try:
        session = await browser_manager.get_session(session_id)
        result = await BrowserActions.scroll(session.page, direction, amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))