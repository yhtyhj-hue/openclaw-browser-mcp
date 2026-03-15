import re
from typing import Optional, Dict
from playwright.async_api import Page
from app.logger import setup_logger

logger = setup_logger(__name__)

class CaptchaDetector:
    """验证码检测器 - 自动识别页面中的验证码类型"""
    
    # 验证码特征库
    CAPTCHA_SIGNATURES = {
        'recaptcha_v2': {
            'selectors': ['[data-sitekey]', '.g-recaptcha', 'iframe[src*="recaptcha"]'],
            'patterns': [r'recaptcha', r'google\.com/recaptcha'],
        },
        'recaptcha_v3': {
            'selectors': ['[data-sitekey][data-size="invisible"]'],
            'patterns': [r'recaptcha.*v3'],
        },
        'hcaptcha': {
            'selectors': ['[data-sitekey][data-sitekey*="site"]', 'iframe[src*="hcaptcha"]'],
            'patterns': [r'hcaptcha', r'hcaptcha\.com'],
        },
        'image': {
            'selectors': ['img[alt*="captcha" i]', '[class*="captcha"] img', '.captcha-image'],
            'patterns': [r'captcha.*image', r'image.*code'],
        },
        'slider': {
            'selectors': ['[class*="slider"]', '[class*="slide"]', '.geetest_slider'],
            'patterns': [r'geetest', r'slider.*captcha', r'slide.*verify'],
        },
        'click': {
            'selectors': ['[class*="point"]', '[class*="click"]', '[class*="select"]'],
            'patterns': [r'click.*captcha', r'point.*select'],
        }
    }
    
    @staticmethod
    async def detect(page: Page) -> Optional[Dict]:
        """
        检测页面中的验证码
        
        Returns:
            验证码信息字典，包含类型、位置、处理建议等
        """
        try:
            logger.info("Detecting captcha...")
            
            # 检查页面HTML中是否包含已知的验证码特征
            html = await page.content()
            
            for captcha_type, signatures in CaptchaDetector.CAPTCHA_SIGNATURES.items():
                # 检查选择器
                for selector in signatures['selectors']:
                    element = await page.query_selector(selector)
                    if element:
                        info = await CaptchaDetector._extract_captcha_info(page, captcha_type, element)
                        logger.info(f"CAPTCHA detected: {captcha_type}")
                        return info
                
                # 检查正则模式
                for pattern in signatures['patterns']:
                    if re.search(pattern, html, re.IGNORECASE):
                        logger.info(f"CAPTCHA pattern matched: {captcha_type}")
                        return {
                            'type': captcha_type,
                            'detected': True,
                            'confidence': 0.7,
                        }
            
            logger.info("No captcha detected")
            return None
            
        except Exception as e:
            logger.error(f"Error during captcha detection: {e}")
            return None
    
    @staticmethod
    async def _extract_captcha_info(page: Page, captcha_type: str, element) -> Dict:
        """提取验证码详细信息"""
        try:
            box = await element.bounding_box()
            
            info = {
                'type': captcha_type,
                'detected': True,
                'element': element,
                'confidence': 0.95,
            }
            
            if box:
                info['location'] = {
                    'x': box['x'],
                    'y': box['y'],
                    'width': box['width'],
                    'height': box['height'],
                }
            
            # 提取特定类型的信息
            if captcha_type == 'recaptcha_v2':
                site_key = await element.get_attribute('data-sitekey')
                if site_key:
                    info['site_key'] = site_key
            
            elif captcha_type == 'image':
                src = await element.get_attribute('src')
                if src:
                    info['image_url'] = src
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting captcha info: {e}")
            return {
                'type': captcha_type,
                'detected': True,
                'error': str(e),
            }
    
    @staticmethod
    async def detect_image_captcha(page: Page) -> Optional[str]:
        """检测并获取图片验证码URL"""
        try:
            captcha_img = await page.query_selector('img[alt*="captcha" i], .captcha-image img')
            if captcha_img:
                src = await captcha_img.get_attribute('src')
                logger.info(f"Image captcha found: {src}")
                return src
            return None
        except Exception as e:
            logger.error(f"Error detecting image captcha: {e}")
            return None
    
    @staticmethod
    async def detect_slider_captcha(page: Page) -> Optional[Dict]:
        """检测滑块验证码"""
        try:
            slider = await page.query_selector('[class*="slider"], .geetest_slider, [class*="slide"]')
            if slider:
                box = await slider.bounding_box()
                logger.info("Slider captcha detected")
                return {
                    'type': 'slider',
                    'element': slider,
                    'location': box,
                }
            return None
        except Exception as e:
            logger.error(f"Error detecting slider: {e}")
            return None
    
    @staticmethod
    async def is_captcha_present(page: Page) -> bool:
        """快速检查是否存在任何验证码"""
        try:
            captcha_selectors = [
                '[data-sitekey]',
                '.g-recaptcha',
                'iframe[src*="recaptcha"]',
                'img[alt*="captcha"]',
                '[class*="captcha"]',
                '[class*="slider"]',
            ]
            
            for selector in captcha_selectors:
                element = await page.query_selector(selector)
                if element:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking captcha presence: {e}")
            return False