import asyncio
from typing import Dict, List, Optional
from playwright.async_api import Page
from app.browser.human_behavior import HumanBehavior
from app.logger import setup_logger

logger = setup_logger(__name__)

class BrowserActions:
    """浏览器操作封装"""
    
    @staticmethod
    async def navigate(page: Page, url: str, wait_until: str = "networkidle") -> Dict:
        """
        导航到URL
        
        Args:
            page: Playwright page
            url: 目标URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
        
        Returns:
            导航结果
        """
        try:
            response = await page.goto(url, wait_until=wait_until)
            
            title = await page.title()
            current_url = page.url
            
            logger.info(f"Navigated to {url} - Title: {title}")
            
            return {
                "status": "success",
                "url": current_url,
                "title": title,
                "status_code": response.status if response else None,
            }
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    @staticmethod
    async def click(page: Page, selector: str, use_human_behavior: bool = True) -> Dict:
        """点击元素"""
        try:
            if use_human_behavior:
                await HumanBehavior.human_like_click(page, selector)
            else:
                await page.click(selector)
            
            logger.info(f"Clicked: {selector}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Click failed for {selector}: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def input_text(page: Page, selector: str, text: str, 
                        use_human_behavior: bool = True) -> Dict:
        """输入文本"""
        try:
            if use_human_behavior:
                await HumanBehavior.human_like_type(page, selector, text)
            else:
                await page.fill(selector, text)
            
            logger.info(f"Typed in {selector}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Input failed for {selector}: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def submit_form(page: Page, form_selector: str = "form") -> Dict:
        """提交表单"""
        try:
            await page.locator(form_selector).evaluate("el => el.submit()")
            await asyncio.sleep(1)  # 等待提交完成
            logger.info(f"Form submitted: {form_selector}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Form submission failed: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def get_screenshot(page: Page, full_page: bool = True) -> bytes:
        """获取页面截图"""
        try:
            screenshot = await page.screenshot(full_page=full_page)
            logger.info("Screenshot captured")
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            raise
    
    @staticmethod
    async def get_html(page: Page) -> str:
        """获取页面HTML"""
        try:
            html = await page.content()
            logger.info("HTML retrieved")
            return html
        except Exception as e:
            logger.error(f"Failed to get HTML: {e}")
            raise
    
    @staticmethod
    async def get_text(page: Page) -> str:
        """获取页面文本内容"""
        try:
            text = await page.evaluate("document.body.innerText")
            logger.info("Text retrieved")
            return text
        except Exception as e:
            logger.error(f"Failed to get text: {e}")
            raise
    
    @staticmethod
    async def get_elements(page: Page) -> List[Dict]:
        """
        获取所有可交互元素
        
        Returns:
            元素列表，包含选择器、标签、文本等
        """
        try:
            elements = await page.evaluate("""
                () => {
                    const interactive = ['button', 'a', 'input', 'select', 'textarea', '[onclick]'];
                    const elements = [];
                    
                    interactive.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                elements.push({
                                    tag: el.tagName,
                                    type: el.type || null,
                                    text: el.innerText?.substring(0, 100) || el.value || '',
                                    class: el.className,
                                    id: el.id,
                                    selector: el.id ? `#${el.id}` : `.${el.className.split(' ')[0]}`,
                                    visible: true,
                                });
                            }
                        });
                    });
                    
                    return elements;
                }
            """)
            
            logger.info(f"Found {len(elements)} interactive elements")
            return elements
        except Exception as e:
            logger.error(f"Failed to get elements: {e}")
            return []
    
    @staticmethod
    async def scroll(page: Page, direction: str = "down", amount: int = 500) -> Dict:
        """
        滚动页面
        
        Args:
            page: Playwright page
            direction: 滚动方向 (up, down)
            amount: 滚动距离（像素）
        
        Returns:
            滚动结果
        """
        try:
            if direction == "down":
                await page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await page.evaluate(f"window.scrollBy(0, {-amount})")
            
            await asyncio.sleep(0.5)
            logger.info(f"Scrolled {direction} by {amount}px")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def wait_for_element(page: Page, selector: str, timeout: int = 5000) -> Dict:
        """等待元素出现"""
        try:
            await page.locator(selector).wait_for(timeout=timeout)
            logger.info(f"Element appeared: {selector}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Timeout waiting for {selector}: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def get_page_info(page: Page) -> Dict:
        """获取页面信息"""
        try:
            return {
                "url": page.url,
                "title": await page.title(),
                "cookies": await page.context.cookies(),
            }
        except Exception as e:
            logger.error(f"Failed to get page info: {e}")
            raise