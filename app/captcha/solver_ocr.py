import io
import base64
import asyncio
from typing import Optional
from playwright.async_api import Page
import pytesseract
from PIL import Image
import cv2
import numpy as np
from app.logger import setup_logger

logger = setup_logger(__name__)

class OCRSolver:
    """OCR 验证码求解器"""
    
    @staticmethod
    async def solve_image_captcha(page: Page,
                                 captcha_img_selector: str = 'img[alt*="captcha"]',
                                 input_selector: str = 'input[name*="captcha"]',
                                 submit_selector: Optional[str] = None) -> bool:
        """
        使用 OCR 解决图片验证码
        
        Args:
            page: Playwright page
            captcha_img_selector: 验证码图片选择器
            input_selector: 验证码输入框选择器
            submit_selector: 提交按钮选择器
        
        Returns:
            是否成功
        """
        try:
            logger.info("Starting OCR captcha solving...")
            
            # 获取验证码图片
            img_element = await page.query_selector(captcha_img_selector)
            if not img_element:
                logger.error(f"Captcha image not found: {captcha_img_selector}")
                return False
            
            # 获取图片数据
            image_data = await img_element.screenshot()
            
            # 识别文字
            captcha_text = await OCRSolver._recognize_text(image_data)
            
            if not captcha_text:
                logger.error("Failed to recognize captcha text")
                return False
            
            logger.info(f"Recognized captcha text: {captcha_text}")
            
            # 填入识别结果
            input_element = await page.query_selector(input_selector)
            if not input_element:
                logger.error(f"Input element not found: {input_selector}")
                return False
            
            await input_element.click()
            await asyncio.sleep(0.3)
            await input_element.fill(captcha_text)
            
            logger.info("Captcha text filled")
            
            # 如果提供了提交按钮，则提交
            if submit_selector:
                submit_btn = await page.query_selector(submit_selector)
                if submit_btn:
                    await submit_btn.click()
                    await asyncio.sleep(2)
                    logger.info("Form submitted")
            
            return True
            
        except Exception as e:
            logger.error(f"Error solving image captcha: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def _recognize_text(image_data: bytes) -> Optional[str]:
        """
        使用 OCR 识别图片中的文字
        
        Args:
            image_data: 图片二进制数据
        
        Returns:
            识别的文字
        """
        try:
            # 转换为 PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # 预处理图片以提高OCR准确率
            image = OCRSolver._preprocess_image(image)
            
            # 使用 Tesseract OCR
            text = pytesseract.image_to_string(
                image,
                config='--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            )
            
            # 清理识别结果
            text = text.strip()
            text = ''.join(text.split())  # 移除空白
            
            # 过滤异常长的结果
            if len(text) > 20:
                text = text[:20]
            
            logger.info(f"OCR result: {text}")
            return text if text else None
            
        except Exception as e:
            logger.error(f"Error in OCR recognition: {e}")
            return None
    
    @staticmethod
    def _preprocess_image(image: Image.Image) -> Image.Image:
        """预处理图片以提高OCR准确率"""
        try:
            # 转换为 OpenCV 格式
            img_array = np.array(image)
            
            # 转换为灰度
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # 提高对比度
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # 二值化
            _, binary = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY)
            
            # 转换回 PIL Image
            result = Image.fromarray(binary)
            return result
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    @staticmethod
    async def recognize_text_from_screenshot(screenshot_path: str) -> Optional[str]:
        """从截图文件识别文字"""
        try:
            image = Image.open(screenshot_path)
            image = OCRSolver._preprocess_image(image)
            text = pytesseract.image_to_string(image)
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"Error recognizing text from screenshot: {e}")
            return None