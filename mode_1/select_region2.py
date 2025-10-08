#!/usr/bin/env python3
"""
使用 tkinter 实现的屏幕区域选择工具
允许用户通过鼠标在屏幕上绘制矩形区域来选择检测区域
用于优化性能，只在指定区域内检测动画效果

相比 select_region.py，这个版本：
1. 不使用 OpenCV 窗口
2. 使用 tkinter 实现更原生的体验
3. 提供更好的跨平台兼容性
"""

import tkinter as tk
from PIL import ImageGrab
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

__all__ = ['select_region']


class RegionSelector:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.root = tk.Tk()
        self.root.title("区域选择器")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 设置透明度
        self.root.configure(bg='gray')
        self.root.config(cursor="crosshair")
        
        # 绑定事件
        self.root.bind('<Button-1>', self.on_button_press)
        self.root.bind('<B1-Motion>', self.on_mouse_drag)
        self.root.bind('<ButtonRelease-1>', self.on_button_release)
        self.root.bind('<KeyPress>', self.on_key_press)
        
        # 创建画布
        self.canvas = tk.Canvas(self.root, cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 初始化变量
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selected_region = None
        
        # 显示提示信息
        self.show_instructions()

    def show_instructions(self):
        """显示操作说明"""
        self.canvas.delete("instruction")
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            50,
            text=f"拖拽选择区域\n按 Enter 确认选择，按 ESC 取消\n屏幕分辨率: {self.screen_width}x{self.screen_height}",
            fill="white",
            font=("Arial", 16),
            tags="instruction"
        )

    def on_button_press(self, event):
        """鼠标按下事件"""
        # 删除之前的矩形
        if self.rect:
            self.canvas.delete(self.rect)
            
        # 限制坐标在屏幕范围内
        self.start_x = max(0, min(event.x, self.screen_width))
        self.start_y = max(0, min(event.y, self.screen_height))
        
        # 创建新的矩形
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2, dash=(4, 2)
        )

    def on_mouse_drag(self, event):
        """鼠标拖拽事件"""
        if self.rect:
            # 限制坐标在屏幕范围内
            current_x = max(0, min(event.x, self.screen_width))
            current_y = max(0, min(event.y, self.screen_height))
            
            # 更新矩形大小
            self.canvas.coords(
                self.rect,
                self.start_x, self.start_y,
                current_x, current_y
            )

    def on_button_release(self, event):
        """鼠标释放事件"""
        pass

    def on_key_press(self, event):
        """键盘按键事件"""
        if event.keysym == 'Return':
            # 确认选择
            if self.rect and self.start_x is not None and self.start_y is not None:
                # 获取当前鼠标位置并限制在屏幕范围内
                current_x = max(0, min(self.root.winfo_pointerx() - self.root.winfo_rootx(), self.screen_width))
                current_y = max(0, min(self.root.winfo_pointery() - self.root.winfo_rooty(), self.screen_height))
                
                # 标准化坐标
                x1, x2 = sorted([self.start_x, current_x])
                y1, y2 = sorted([self.start_y, current_y])
                
                # 保存选区 (相对于整个屏幕)
                self.selected_region = (int(x1), int(y1), int(x2), int(y2))
                
                # 计算宽度和高度
                width = x2 - x1
                height = y2 - y1
                
                if width > 0 and height > 0:
                    logger.info(f"选定区域: x={self.selected_region[0]}, y={self.selected_region[1]}, "
                                f"width={width}, height={height}")
                    self.root.quit()
                else:
                    logger.warning("选择的区域太小，请重新选择")
                    
        elif event.keysym == 'Escape':
            # 取消选择
            self.selected_region = None
            self.root.quit()

    def run(self):
        """运行选择器"""
        self.root.mainloop()
        self.root.destroy()
        
        if self.selected_region:
            x1, y1, x2, y2 = self.selected_region
            return (x1, y1, x2 - x1, y2 - y1)  # 返回 (x, y, width, height) 格式
        return None


def select_region():
    """
    让用户选择屏幕上的一个区域（使用 tkinter 实现）
    
    Returns:
        tuple: (x, y, width, height) 选择的区域坐标，如果未选择则返回None
    """
    logger.info("启动基于 tkinter 的区域选择器...")
    
    try:
        # 截取屏幕以获取分辨率信息
        screenshot = ImageGrab.grab()
        screen_width, screen_height = screenshot.size
        logger.info(f"屏幕分辨率: {screen_width}x{screen_height}")
        screenshot.close()
    except Exception as e:
        logger.error(f"无法获取屏幕信息: {e}")
        return None
    
    # 创建并运行选择器
    selector = RegionSelector(screen_width, screen_height)
    result = selector.run()
    
    # 验证区域是否在屏幕范围内
    if result:
        x, y, w, h = result
        if x < 0 or y < 0 or x + w > screen_width or y + h > screen_height:
            logger.error(f"选定区域 ({x}, {y}, {w}, {h}) 超出屏幕范围 (0, 0, {screen_width}, {screen_height})")
            return None
        logger.info(f"区域验证通过: ({x}, {y}, {w}, {h}) 在屏幕范围 (0, 0, {screen_width}, {screen_height}) 内")
    
    return result


if __name__ == "__main__":
    region = select_region()
    if region:
        x, y, w, h = region
        logger.info("成功选择区域:")
        logger.info(f"  左上角坐标: ({x}, {y})")
        logger.info(f"  宽度: {w}")
        logger.info(f"  高度: {h}")
        logger.info(f"  区域坐标: ({x}, {y}, {x + w}, {y + h})")
    else:
        logger.info("未选择区域或程序被取消")