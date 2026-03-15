from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import uuid
from app.main import browser_manager
from app.browser.browser_actions import BrowserActions
from app.browser.human_behavior import HumanBehavior
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# 工作流存储（实际应用中应使用数据库）
WORKFLOWS = {}

class WorkflowStep(BaseModel):
    """工作流步骤"""
    action: str  # navigate, click, input, screenshot, wait, etc.
    selector: Optional[str] = None
    value: Optional[str] = None
    wait_time: float = 0
    timeout: int = 5000
    description: Optional[str] = None

class WorkflowRequest(BaseModel):
    """工作流请求"""
    name: str
    steps: List[WorkflowStep]
    description: Optional[str] = None

class WorkflowExecuteRequest(BaseModel):
    """执行工作流请求"""
    workflow_id: str
    session_id: str

@router.post("/{session_id}/workflow/create")
async def create_workflow(session_id: str, req: WorkflowRequest = Body(...)):
    """
    创建工作流
    
    工作流是一系列步骤的集合，可以重复执行
    """
    try:
        workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
        
        workflow = {
            "id": workflow_id,
            "name": req.name,
            "description": req.description,
            "steps": req.steps,
            "created_at": None,
            "executed_count": 0,
        }
        
        WORKFLOWS[workflow_id] = workflow
        
        logger.info(f"Workflow created: {workflow_id}")
        return {
            "status": "success",
            "workflow_id": workflow_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/workflow/list")
async def list_workflows(session_id: str):
    """列出所有工作流"""
    try:
        workflows = [
            {
                "id": wf["id"],
                "name": wf["name"],
                "steps_count": len(wf["steps"]),
                "executed_count": wf["executed_count"],
            }
            for wf in WORKFLOWS.values()
        ]
        
        return {
            "count": len(workflows),
            "workflows": workflows,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/workflow/execute")
async def execute_workflow(session_id: str, req: WorkflowExecuteRequest = Body(...)):
    """
    执行工作流
    
    按顺序执行工作流中的所有步骤
    """
    try:
        session = await browser_manager.get_session(session_id)
        
        if req.workflow_id not in WORKFLOWS:
            raise Exception(f"Workflow not found: {req.workflow_id}")
        
        workflow = WORKFLOWS[req.workflow_id]
        steps_results = []
        
        logger.info(f"Executing workflow: {req.workflow_id}")
        
        for i, step in enumerate(workflow["steps"]):
            try:
                step_result = await _execute_step(session.page, step, i)
                steps_results.append(step_result)
                
                if step.wait_time > 0:
                    await asyncio.sleep(step.wait_time)
                    
            except Exception as e:
                logger.error(f"Step {i} failed: {e}")
                steps_results.append({
                    "step": i,
                    "action": step.action,
                    "status": "error",
                    "error": str(e),
                })
                
                # 可选：在第一个失败处停止或继续
                # break
        
        workflow["executed_count"] += 1
        
        successful_steps = sum(1 for r in steps_results if r["status"] == "success")
        
        logger.info(f"Workflow execution completed: {successful_steps}/{len(steps_results)} steps")
        
        return {
            "status": "success",
            "workflow_id": req.workflow_id,
            "successful_steps": successful_steps,
            "total_steps": len(steps_results),
            "steps": steps_results,
        }
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _execute_step(page, step: WorkflowStep, step_index: int) -> Dict[str, Any]:
    """执行单个工作流步骤"""
    
    try:
        if step.action == "navigate":
            await BrowserActions.navigate(page, step.value)
            return {
                "step": step_index,
                "action": step.action,
                "status": "success",
            }
        
        elif step.action == "click":
            await HumanBehavior.human_like_click(page, step.selector)
            return {
                "step": step_index,
                "action": step.action,
                "selector": step.selector,
                "status": "success",
            }
        
        elif step.action == "input":
            await HumanBehavior.human_like_type(page, step.selector, step.value)
            return {
                "step": step_index,
                "action": step.action,
                "selector": step.selector,
                "status": "success",
            }
        
        elif step.action == "screenshot":
            screenshot = await BrowserActions.get_screenshot(page)
            return {
                "step": step_index,
                "action": step.action,
                "status": "success",
                "screenshot_size": len(screenshot),
            }
        
        elif step.action == "wait":
            if step.selector:
                await BrowserActions.wait_for_element(page, step.selector, step.timeout)
            else:
                await asyncio.sleep(step.wait_time)
            return {
                "step": step_index,
                "action": step.action,
                "status": "success",
            }
        
        elif step.action == "scroll":
            await BrowserActions.scroll(page, "down", int(step.value or 500))
            return {
                "step": step_index,
                "action": step.action,
                "status": "success",
            }
        
        elif step.action == "submit":
            await BrowserActions.submit_form(page, step.selector)
            return {
                "step": step_index,
                "action": step.action,
                "status": "success",
            }
        
        else:
            raise Exception(f"Unknown action: {step.action}")
            
    except Exception as e:
        raise Exception(f"Step execution failed: {e}")