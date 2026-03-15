from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from app.main import browser_manager
from app.captcha.detector import CaptchaDetector
from app.captcha.slider_solver import SliderSolver
from app.captcha.solver_ocr import OCRSolver
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class CaptchaSolveRequest(BaseModel):
    auto_retry: bool = True
    max_attempts: int = 3
    timeout: int = 60

@router.post("/{session_id}/captcha/detect")
async def detect_captcha(session_id: str):
    """检测页面中的验证码"""
    try:
        session = await browser_manager.get_session(session_id)
        captcha_info = await CaptchaDetector.detect(session.page)
        
        if captcha_info:
            return {
                "detected": True,
                "type": captcha_info.get('type'),
                "confidence": captcha_info.get('confidence', 0),
                "location": captcha_info.get('location'),
            }
        else:
            return {"detected": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/captcha/solve")
async def solve_captcha(session_id: str, req: CaptchaSolveRequest = Body(...)):
    """自动检测并解决验证码"""
    try:
        session = await browser_manager.get_session(session_id)
        
        attempts = 0
        while attempts < req.max_attempts:
            attempts += 1
            logger.info(f"CAPTCHA solve attempt {attempts}/{req.max_attempts}")
            
            # 检测验证码类型
            captcha_info = await CaptchaDetector.detect(session.page)
            
            if not captcha_info:
                logger.info("No captcha detected")
                return {
                    "status": "no_captcha",
                    "message": "No captcha detected on page",
                }
            
            captcha_type = captcha_info.get('type')
            logger.info(f"Captcha type: {captcha_type}")
            
            # 根据类型处理
            success = False
            
            if captcha_type == 'slider':
                success = await SliderSolver.solve(session.page)
            elif captcha_type == 'image':
                success = await OCRSolver.solve_image_captcha(session.page)
            elif captcha_type in ['recaptcha_v2', 'recaptcha_v3', 'hcaptcha']:
                logger.warning(f"Advanced captcha {captcha_type} requires manual handling or external service")
                return {
                    "status": "unsupported",
                    "captcha_type": captcha_type,
                    "message": "This captcha type requires external service or manual intervention",
                }
            else:
                logger.warning(f"Unknown captcha type: {captcha_type}")
            
            if success:
                return {
                    "status": "success",
                    "captcha_type": captcha_type,
                    "attempts": attempts,
                }
            elif not req.auto_retry or attempts >= req.max_attempts:
                return {
                    "status": "failed",
                    "captcha_type": captcha_type,
                    "attempts": attempts,
                }
        
        return {
            "status": "failed",
            "message": "All retry attempts exhausted",
        }
        
    except Exception as e:
        logger.error(f"Error solving captcha: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))