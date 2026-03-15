from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from app.main import browser_manager
from app.browser.browser_actions import BrowserActions
from app.browser.human_behavior import HumanBehavior
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class FormFillRequest(BaseModel):
    """表单填充请求"""
    fields: List[dict]  # [{"selector": "...", "value": "..."}]
    submit_selector: Optional[str] = None
    use_human_behavior: bool = True

class MultiClickRequest(BaseModel):
    """多步骤点击请求"""
    steps: List[dict]  # [{"selector": "...", "wait": 2}]

class WaitRequest(BaseModel):
    """等待请求"""
    selector: Optional[str] = None
    timeout: int = 5000
    condition: str = "visible"  # visible, hidden, attached

@router.post("/{session_id}/interaction/fill-form")
async def fill_form(session_id: str, req: FormFillRequest = Body(...)):
    """
    填充表单
    
    示例请求:
    {
        "fields": [
            {"selector": "input[name=username]", "value": "user@example.com"},
            {"selector": "input[name=password]", "value": "password123"}
        ],
        "submit_selector": "button[type=submit]"
    }
    """
    try:
        session = await browser_manager.get_session(session_id)
        results = []
        
        # 填充每个字段
        for field in req.fields:
            selector = field.get("selector")
            value = field.get("value")
            
            if not selector or value is None:
                results.append({"selector": selector, "status": "skipped"})
                continue
            
            try:
                if req.use_human_behavior:
                    await HumanBehavior.human_like_type(session.page, selector, str(value))
                else:
                    await session.page.fill(selector, str(value))
                
                results.append({"selector": selector, "status": "success"})
            except Exception as e:
                logger.error(f"Failed to fill {selector}: {e}")
                results.append({"selector": selector, "status": "error", "error": str(e)})
        
        # 如果提供了提交选择器，则提交
        if req.submit_selector:
            try:
                await HumanBehavior.human_like_click(session.page, req.submit_selector)
                results.append({"selector": req.submit_selector, "status": "submitted"})
            except Exception as e:
                logger.error(f"Failed to submit form: {e}")
                results.append({"selector": req.submit_selector, "status": "error", "error": str(e)})
        
        return {
            "status": "success",
            "fields_filled": sum(1 for r in results if r["status"] == "success"),
            "results": results,
        }
        
    except Exception as e:
        logger.error(f"Form filling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/interaction/multi-click")
async def multi_click(session_id: str, req: MultiClickRequest = Body(...)):
    """
    执行多步骤点击交互
    
    示例请求:
    {
        "steps": [
            {"selector": "button.menu", "wait": 1},
            {"selector": "a.logout", "wait": 0}
        ]
    }
    """
    try:
        session = await browser_manager.get_session(session_id)
        results = []
        
        for i, step in enumerate(req.steps):
            selector = step.get("selector")
            wait_time = step.get("wait", 1)
            
            try:
                await HumanBehavior.human_like_click(session.page, selector)
                results.append({
                    "step": i,
                    "selector": selector,
                    "status": "success",
                })
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                logger.error(f"Click step {i} failed: {e}")
                results.append({
                    "step": i,
                    "selector": selector,
                    "status": "error",
                    "error": str(e),
                })
        
        return {
            "status": "success",
            "successful_steps": sum(1 for r in results if r["status"] == "success"),
            "results": results,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/interaction/wait")
async def wait_for_element(session_id: str, req: WaitRequest):
    """
    等待元素出现/消失/加载
    
    condition: "visible" (元素可见), "hidden" (元素隐藏), "attached" (DOM中存在)
    """
    try:
        session = await browser_manager.get_session(session_id)
        
        if req.selector:
            locator = session.page.locator(req.selector)
            
            if req.condition == "visible":
                await locator.wait_for(state="visible", timeout=req.timeout)
            elif req.condition == "hidden":
                await locator.wait_for(state="hidden", timeout=req.timeout)
            elif req.condition == "attached":
                await locator.wait_for(state="attached", timeout=req.timeout)
            else:
                raise ValueError(f"Unknown condition: {req.condition}")
        
        return {
            "status": "success",
            "message": f"Element {req.condition}: {req.selector}",
        }
        
    except Exception as e:
        logger.error(f"Wait failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/interaction/keyboard")
async def keyboard_event(session_id: str, key: str = Body(...)):
    """
    发送键盘事件
    
    支持: Enter, Tab, Escape, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, etc.
    """
    try:
        session = await browser_manager.get_session(session_id)
        await session.page.keyboard.press(key)
        
        return {
            "status": "success",
            "key": key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/interaction/hover")
async def hover_element(session_id: str, selector: str = Body(...)):
    """悬停在元素上"""
    try:
        session = await browser_manager.get_session(session_id)
        await session.page.locator(selector).hover()
        
        return {
            "status": "success",
            "selector": selector,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/interaction/double-click")
async def double_click_element(session_id: str, selector: str = Body(...)):
    """双击元素"""
    try:
        session = await browser_manager.get_session(session_id)
        await HumanBehavior.human_like_click(session.page, selector, double=True)
        
        return {
            "status": "success",
            "selector": selector,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/interaction/right-click")
async def right_click_element(session_id: str, selector: str = Body(...)):
    """右键点击元素"""
    try:
        session = await browser_manager.get_session(session_id)
        await HumanBehavior.human_like_click(session.page, selector, button="right")
        
        return {
            "status": "success",
            "selector": selector,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))