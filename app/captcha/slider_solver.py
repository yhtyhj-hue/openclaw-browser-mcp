import asyncio
import random
import math
from typing import List, Tuple
from playwright.async_api import Page
from app.browser.human_behavior import HumanBehavior
from app.logger import setup_logger

logger = setup_logger(__name__)

class SliderSolver:
    """滑块验证码求解器"""
    
    @staticmethod
    def generate_slider_trajectory(distance: float, 
                                  duration: float = 2.0,
                                  overshoot: bool = True) -> List[Tuple[float, float]]:
        """
        生成滑块轨迹
        
        Args:
            distance: 需要滑动的距离（像素）
            duration: 总耗时（秒）
            overshoot: 是否超过然后返回（更真实）
        
        Returns:
            [(x_offset, delay), ...] 轨迹点列表
        """
        steps = int(duration * 60)  # 60Hz 采样
        
        # 计算加速度曲线（ease-in-out）
        t_values = [i / steps for i in range(steps + 1)]
        accel_curve = [
            t if t < 0.5 else 1 - (1 - t) ** 2
            for t in [(2 * t ** 2 if t < 0.5 else 1 - 2 * (1 - t) ** 2) for t in t_values]
        ]
        
        # 计算超出距离
        overshoot_amount = random.randint(5, 20) if overshoot else 0
        total_distance = distance + overshoot_amount
        
        trajectory = []
        current_x = 0
        
        # 生成前进轨迹
        for i, t in enumerate(t_values[:-1]):
            # 加速度曲线应用
            ease_t = (2 * t ** 2) if t < 0.5 else (1 - 2 * (1 - t) ** 2)
            
            # 计算该步骤应该移动的距离
            target_x = ease_t * total_distance
            step_distance = target_x - current_x
            
            # 添加微小抖动
            step_distance += random.uniform(-1, 1)
            current_x += step_distance
            
            # 计算延迟
            delay = (duration / steps) * 1000 + random.uniform(-20, 20)
            delay = max(10, delay)
            
            trajectory.append((current_x, delay))
        
        # 如果有超出，生成修正轨迹
        if overshoot and overshoot_amount > 0:
            correction_steps = random.randint(8, 15)
            for i in range(correction_steps):
                # 逐步回到目标位置
                current_x -= overshoot_amount / correction_steps
                current_x += random.uniform(-0.5, 0.5)
                delay = 50 + random.uniform(-20, 20)
                trajectory.append((current_x, delay))
        
        # 确保最后一个点到达目标
        trajectory[-1] = (distance, trajectory[-1][1])
        
        return trajectory
    
    @staticmethod
    async def solve(page: Page, 
                   slider_selector: str = '.geetest_slider',
                   track_selector: str = '.geetest_track_fill',
                   timeout: int = 30) -> bool:
        """
        解决滑块验证码
        
        Args:
            page: Playwright page
            slider_selector: 滑块选择器
            track_selector: 轨迹选择器
            timeout: 超时时间（秒）
        
        Returns:
            是否成功
        """
        try:
            logger.info("Starting slider solving...")
            
            # 获取滑块元素
            slider = await page.query_selector(slider_selector)
            if not slider:
                logger.error(f"Slider not found: {slider_selector}")
                return False
            
            # 获取滑块位置
            slider_box = await slider.bounding_box()
            if not slider_box:
                logger.error("Could not get slider bounding box")
                return False
            
            logger.info(f"Slider size: {slider_box['width']} x {slider_box['height']}")
            
            # 估计需要滑动的距离（通常是滑块宽度的大部分）
            # 这是一个启发式估计，实际距离可能需要根据具体验证码调整
            estimated_distance = slider_box['width'] * 0.8
            
            # 生成轨迹
            trajectory = SliderSolver.generate_slider_trajectory(
                estimated_distance,
                duration=random.uniform(1.5, 3.0),
                overshoot=True
            )
            
            logger.info(f"Generated {len(trajectory)} trajectory points")
            
            # 获取滑块内部拖拽元素的位置
            drag_handle = await page.query_selector(f'{slider_selector} .geetest_slider_button')
            if not drag_handle:
                drag_handle = slider  # 备选方案
            
            handle_box = await drag_handle.bounding_box()
            if not handle_box:
                logger.error("Could not get handle bounding box")
                return False
            
            start_x = handle_box['x'] + handle_box['width'] / 2
            start_y = handle_box['y'] + handle_box['height'] / 2
            
            logger.info(f"Starting drag from ({start_x}, {start_y})")
            
            # 执行拖拽
            await page.mouse.move(start_x, start_y)
            await asyncio.sleep(random.uniform(0.2, 0.5))  # 真人停顿
            
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # 沿轨迹拖动
            current_x = start_x
            for relative_x, delay in trajectory:
                target_x = start_x + relative_x
                await page.mouse.move(target_x, start_y)
                await asyncio.sleep(delay / 1000)
                current_x = target_x
            
            await asyncio.sleep(random.uniform(0.2, 0.4))
            await page.mouse.up()
            
            logger.info("Slider drag completed")
            
            # 等待验证完成
            await asyncio.sleep(2)
            
            # 检查是否验证成功
            success = await SliderSolver._check_slider_success(page)
            
            if success:
                logger.info("Slider captcha solved successfully!")
            else:
                logger.warning("Slider may not have been solved correctly")
            
            return success
            
        except Exception as e:
            logger.error(f"Error solving slider: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def _check_slider_success(page: Page) -> bool:
        """检查滑块是否成功验证"""
        try:
            # 检查成功标志（这些选择器可能因网站而异）
            success_indicators = [
                '.geetest_success',
                '.success-notice',
                '[class*="success"]',
                'img[alt*="success"]',
            ]
            
            for indicator in success_indicators:
                element = await page.query_selector(indicator)
                if element:
                    visibility = await element.is_visible()
                    if visibility:
                        return True
            
            # 检查是否没有错误标志
            error_indicators = [
                '.geetest_error',
                '[class*="error"]',
                'img[alt*="fail"]',
            ]
            
            for indicator in error_indicators:
                element = await page.query_selector(indicator)
                if element:
                    visibility = await element.is_visible()
                    if visibility:
                        return False
            
            return True  # 无法确定，假设成功
            
        except Exception as e:
            logger.error(f"Error checking slider success: {e}")
            return True