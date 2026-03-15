import asyncio
import math
import random
from typing import Tuple, List
import numpy as np
from app.logger import setup_logger

logger = setup_logger(__name__)

class HumanBehavior:
    """真人行为模拟器 - 模拟真人的鼠标、键盘、滚动等行为"""
    
    @staticmethod
    def bezier_curve(start: Tuple[float, float], 
                     control: Tuple[float, float], 
                     end: Tuple[float, float], 
                     t: float) -> Tuple[float, float]:
        """二次贝塞尔曲线计算"""
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t ** 2 * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t ** 2 * end[1]
        return x, y
    
    @staticmethod
    def cubic_bezier_curve(points: List[Tuple[float, float]], 
                          t: float) -> Tuple[float, float]:
        """三次贝塞尔曲线"""
        p0, p1, p2, p3 = points
        mt = 1 - t
        
        x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
        y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
        
        return x, y
    
    @staticmethod
    def generate_human_trajectory(start: Tuple[float, float],
                                 end: Tuple[float, float],
                                 duration: float = 1.0,
                                 num_steps: int = 30) -> List[Tuple[float, float, float]]:
        """
        生成真人级别的鼠标轨迹
        
        Args:
            start: 起点坐标 (x, y)
            end: 终点坐标 (x, y)
            duration: 总耗时（秒）
            num_steps: 轨迹点数
        
        Returns:
            轨迹点列表 [(x, y, delay), ...]
        """
        # 生成控制点（随机偏移以增加自然感）
        mid_x = (start[0] + end[0]) / 2 + random.uniform(-80, 80)
        mid_y = (start[1] + end[1]) / 2 + random.uniform(-60, 60)
        control = (mid_x, mid_y)
        
        trajectory = []
        
        for i in range(num_steps + 1):
            t = i / num_steps
            
            # 使用ease-in-out缓动
            ease_t = t ** 2 / (2 * (t ** 2 - t) + 1)
            
            # 计算贝塞尔曲线上的点
            x, y = HumanBehavior.bezier_curve(start, control, end, ease_t)
            
            # 添加微小的抖动（人类的微妙运动）
            x += random.uniform(-2, 2)
            y += random.uniform(-2, 2)
            
            # 计算延迟（变速）
            delay = (duration / num_steps) + random.uniform(-10, 10) / 1000
            delay = max(5, delay)  # 最小5ms
            
            trajectory.append((x, y, delay))
        
        return trajectory
    
    @staticmethod
    async def human_like_move(page, 
                             start: Tuple[float, float],
                             end: Tuple[float, float],
                             duration: float = 1.0):
        """
        模拟真人鼠标移动
        
        Args:
            page: Playwright page 对象
            start: 起点
            end: 终点
            duration: 耗时（秒）
        """
        trajectory = HumanBehavior.generate_human_trajectory(start, end, duration)
        
        for x, y, delay in trajectory:
            await page.mouse.move(x, y)
            await asyncio.sleep(delay / 1000)
    
    @staticmethod
    async def human_like_click(page, selector: str, 
                              button: str = "left",
                              double: bool = False):
        """
        模拟真人点击
        
        Args:
            page: Playwright page
            selector: CSS选择器
            button: 按钮 (left, right, middle)
            double: 是否双击
        """
        try:
            # 获取元素位置
            element_box = await page.locator(selector).bounding_box()
            if not element_box:
                raise Exception(f"Element {selector} not found")
            
            # 计算点击位置（中心 + 随机偏移）
            center_x = element_box["x"] + element_box["width"] / 2
            center_y = element_box["y"] + element_box["height"] / 2
            
            click_x = center_x + random.uniform(-5, 5)
            click_y = center_y + random.uniform(-5, 5)
            
            # 模拟鼠标移动到按钮
            await HumanBehavior.human_like_move(
                page, 
                (random.uniform(100, 200), random.uniform(100, 200)),
                (click_x, click_y),
                duration=random.uniform(0.3, 0.8)
            )
            
            # 等待片刻（真人会停顿）
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # 执行点击
            if double:
                await page.mouse.dclick(click_x, click_y)
            else:
                await page.mouse.click(click_x, click_y, button=button)
            
            await asyncio.sleep(random.uniform(0.1, 0.2))
            logger.debug(f"Clicked element: {selector}")
            
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            raise
    
    @staticmethod
    async def human_like_type(page, selector: str, text: str, 
                             delay: int = 50):
        """
        模拟真人输入
        
        Args:
            page: Playwright page
            selector: CSS选择器
            text: 输入文本
            delay: 字符间延迟（ms）
        """
        try:
            # 点击输入框
            await HumanBehavior.human_like_click(page, selector)
            
            # 清空现有内容
            await asyncio.sleep(random.uniform(0.1, 0.2))
            await page.locator(selector).clear()
            
            # 逐字输入
            for char in text:
                await page.type(selector, char, delay=delay + random.uniform(-20, 20))
                # 偶尔停顿（真人会停下来想）
                if random.random() < 0.1:  # 10% 的概率停顿
                    await asyncio.sleep(random.uniform(0.2, 0.5))
            
            await asyncio.sleep(random.uniform(0.1, 0.3))
            logger.debug(f"Typed text in {selector}")
            
        except Exception as e:
            logger.error(f"Failed to type in element {selector}: {e}")
            raise
    
    @staticmethod
    async def human_like_scroll(page, target_height: float = None,
                               smooth: bool = True):
        """
        模拟真人滚动
        
        Args:
            page: Playwright page
            target_height: 目标滚动高度。若为None则滚动到底部
            smooth: 是否平滑滚动
        """
        try:
            if target_height is None:
                # 滚动到底部
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            else:
                if smooth:
                    # 分段平滑滚动
                    current_scroll = 0
                    while current_scroll < target_height:
                        scroll_amount = random.randint(100, 300)
                        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                        current_scroll += scroll_amount
                else:
                    await page.evaluate(f"window.scrollTo(0, {target_height})")
            
            logger.debug(f"Scrolled to height: {target_height}")
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            raise
    
    @staticmethod
    async def human_like_delay(min_seconds: float = 0.5, 
                              max_seconds: float = 2.0):
        """
        真人级别的随机延迟
        
        Args:
            min_seconds: 最小延迟（秒）
            max_seconds: 最大延迟（秒）
        """
        delay = random.uniform(min_seconds, max_seconds)
        # 偶尔会有更长的停顿
        if random.random() < 0.1:
            delay += random.uniform(1, 3)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def random_mouse_movement(page, times: int = 3):
        """
        随机鼠标移动（看起来在浏览页面）
        
        Args:
            page: Playwright page
            times: 移动次数
        """
        for _ in range(times):
            x = random.uniform(100, 1900)
            y = random.uniform(100, 1000)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.5, 1.5))