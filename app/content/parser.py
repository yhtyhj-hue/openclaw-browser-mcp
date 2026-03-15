from typing import List, Dict, Optional
from playwright.async_api import Page
from app.logger import setup_logger

logger = setup_logger(__name__)

class ContentParser:
    """页面内容解析器"""
    
    @staticmethod
    async def extract_links(page: Page) -> List[Dict]:
        """提取页面所有链接"""
        try:
            links = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a'))
                        .filter(a => a.href)
                        .map(a => ({
                            text: a.innerText?.substring(0, 100) || '',
                            href: a.href,
                            title: a.title,
                            target: a.target,
                        }))
                        .slice(0, 100);
                }
            """)
            return links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    @staticmethod
    async def extract_images(page: Page) -> List[Dict]:
        """提取页面所有图片"""
        try:
            images = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('img'))
                        .map(img => ({
                            src: img.src,
                            alt: img.alt,
                            title: img.title,
                            width: img.width,
                            height: img.height,
                        }))
                        .slice(0, 50);
                }
            """)
            return images
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return []
    
    @staticmethod
    async def extract_forms(page: Page) -> List[Dict]:
        """提取页面所有表单"""
        try:
            forms = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('form'))
                        .map(form => {
                            const fields = Array.from(form.querySelectorAll('input, textarea, select'))
                                .map(f => ({
                                    name: f.name,
                                    type: f.type,
                                    id: f.id,
                                    required: f.required,
                                }));
                            
                            const buttons = Array.from(form.querySelectorAll('button, input[type="submit"]'))
                                .map(b => ({
                                    text: b.innerText || b.value,
                                    type: b.type,
                                }));
                            
                            return {
                                id: form.id,
                                name: form.name,
                                action: form.action,
                                method: form.method,
                                fields: fields,
                                buttons: buttons,
                            };
                        });
                }
            """)
            return forms
        except Exception as e:
            logger.error(f"Error extracting forms: {e}")
            return []
    
    @staticmethod
    async def extract_tables(page: Page) -> List[Dict]:
        """提取页面所有表格"""
        try:
            tables = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('table'))
                        .map(table => {
                            const headers = Array.from(table.querySelectorAll('th'))
                                .map(th => th.innerText);
                            
                            const rows = Array.from(table.querySelectorAll('tr'))
                                .slice(headers.length > 0 ? 1 : 0)
                                .map(tr => Array.from(tr.querySelectorAll('td'))
                                    .map(td => td.innerText)
                                )
                                .slice(0, 10);
                            
                            return {
                                headers: headers,
                                rows: rows,
                                row_count: rows.length,
                            };
                        })
                        .slice(0, 10);
                }
            """)
            return tables
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return []
    
    @staticmethod
    async def find_elements_by_text(page: Page, text: str) -> List[Dict]:
        """根据文本内容查找元素"""
        try:
            elements = await page.evaluate(f"""
                () => {{
                    const searchText = "{text}".toLowerCase();
                    return Array.from(document.querySelectorAll('*'))
                        .filter(el => el.innerText?.toLowerCase().includes(searchText))
                        .map(el => ({{
                            tag: el.tagName,
                            text: el.innerText?.substring(0, 100),
                            class: el.className,
                            id: el.id,
                            type: el.type,
                        }}))
                        .slice(0, 20);
                }}
            """)
            return elements
        except Exception as e:
            logger.error(f"Error finding elements: {e}")
            return []
    
    @staticmethod
    async def get_page_structure(page: Page) -> Dict:
        """获取页面DOM结构摘要"""
        try:
            structure = await page.evaluate("""
                () => {
                    return {
                        title: document.title,
                        headings: {
                            h1: document.querySelectorAll('h1').length,
                            h2: document.querySelectorAll('h2').length,
                            h3: document.querySelectorAll('h3').length,
                        },
                        paragraphs: document.querySelectorAll('p').length,
                        links: document.querySelectorAll('a').length,
                        images: document.querySelectorAll('img').length,
                        forms: document.querySelectorAll('form').length,
                        buttons: document.querySelectorAll('button').length,
                        inputs: document.querySelectorAll('input').length,
                        tables: document.querySelectorAll('table').length,
                    };
                }
            """)
            return structure
        except Exception as e:
            logger.error(f"Error getting page structure: {e}")
            return {}