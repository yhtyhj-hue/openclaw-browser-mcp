from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from app.main import browser_manager
from app.browser.browser_actions import BrowserActions
from app.content.parser import ContentParser
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class ContentExtractRequest(BaseModel):
    extract_text: bool = True
    extract_images: bool = False
    extract_links: bool = True
    extract_forms: bool = True
    extract_tables: bool = True
    include_hidden: bool = False

class ElementInfo(BaseModel):
    tag: str
    text: Optional[str] = None
    attributes: Dict = {}
    visible: bool = True

@router.post("/{session_id}/content/extract")
async def extract_content(session_id: str, req: ContentExtractRequest = Body(...)):
    """
    提取页面内容（结构化）
    
    提取文本、图片、链接、表单、表格等结构化内容
    """
    try:
        session = await browser_manager.get_session(session_id)
        
        result = {
            "status": "success",
            "timestamp": None,
        }
        
        if req.extract_text:
            text = await BrowserActions.get_text(session.page)
            result["text"] = text[:5000]  # 限制大小
        
        if req.extract_links:
            links = await ContentParser.extract_links(session.page)
            result["links"] = links[:50]  # 限制数量
        
        if req.extract_images:
            images = await ContentParser.extract_images(session.page)
            result["images"] = images[:20]
        
        if req.extract_forms:
            forms = await ContentParser.extract_forms(session.page)
            result["forms"] = forms
        
        if req.extract_tables:
            tables = await ContentParser.extract_tables(session.page)
            result["tables"] = tables[:5]
        
        logger.info(f"Content extracted from session {session_id}")
        return result
        
    except Exception as e:
        logger.error(f"Content extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/content/links")
async def get_links(session_id: str):
    """获取页面所有链接"""
    try:
        session = await browser_manager.get_session(session_id)
        links = await ContentParser.extract_links(session.page)
        return {
            "count": len(links),
            "links": links,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/content/images")
async def get_images(session_id: str, limit: int = 50):
    """获取页面所有图片"""
    try:
        session = await browser_manager.get_session(session_id)
        images = await ContentParser.extract_images(session.page)
        return {
            "count": len(images),
            "images": images[:limit],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/content/forms")
async def get_forms(session_id: str):
    """获取页面所有表单"""
    try:
        session = await browser_manager.get_session(session_id)
        forms = await ContentParser.extract_forms(session.page)
        return {
            "count": len(forms),
            "forms": forms,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/content/tables")
async def get_tables(session_id: str):
    """获取页面所有表格"""
    try:
        session = await browser_manager.get_session(session_id)
        tables = await ContentParser.extract_tables(session.page)
        return {
            "count": len(tables),
            "tables": tables,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/content/find-element")
async def find_element(session_id: str, text: str = Body(...)):
    """
    根据文本内容查找元素
    
    示例: 找到所有包含"登录"文本的元素
    """
    try:
        session = await browser_manager.get_session(session_id)
        elements = await ContentParser.find_elements_by_text(session.page, text)
        return {
            "search_text": text,
            "found_count": len(elements),
            "elements": elements,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/content/page-structure")
async def get_page_structure(session_id: str):
    """获取页面DOM结构摘要"""
    try:
        session = await browser_manager.get_session(session_id)
        structure = await ContentParser.get_page_structure(session.page)
        return structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/content/search-text")
async def search_text(session_id: str, query: str = Body(...)):
    """搜索页面文本"""
    try:
        session = await browser_manager.get_session(session_id)
        text = await BrowserActions.get_text(session.page)
        
        # 简单的文本搜索
        lines = text.split('\n')
        results = [line for line in lines if query.lower() in line.lower()]
        
        return {
            "query": query,
            "matches": len(results),
            "results": results[:20],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))