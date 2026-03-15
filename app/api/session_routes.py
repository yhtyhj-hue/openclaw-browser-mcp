import uuid
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from app.main import browser_manager
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class SessionOpenRequest(BaseModel):
    user_agent: Optional[str] = None
    headless: bool = True
    timeout: int = 30000

class SessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: str

@router.post("/open", response_model=SessionResponse)
async def open_session(req: SessionOpenRequest = Body(...)):
    """创建新的浏览器会话"""
    try:
        session_id = await browser_manager.create_session()
        session = await browser_manager.get_session(session_id)
        
        return SessionResponse(
            session_id=session_id,
            status="active",
            created_at=str(session.created_at),
        )
    except Exception as e:
        logger.error(f"Failed to open session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/close")
async def close_session(session_id: str):
    """关闭会话"""
    try:
        await browser_manager.close_session(session_id)
        return {"status": "success", "message": f"Session {session_id} closed"}
    except Exception as e:
        logger.error(f"Failed to close session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_sessions():
    """列出所有活跃会话"""
    return {
        "active_sessions": browser_manager.get_active_sessions_count(),
        "sessions": browser_manager.get_sessions_info(),
    }