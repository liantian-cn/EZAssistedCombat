#!/usr/bin/env python3
"""
允许用户通过鼠标在屏幕上绘制矩形区域来选择检测区域
用于优化性能，只在指定区域内检测动画效果
"""

import cv2
from PIL import Image, ImageGrab, ImageDraw, ImageFont
import numpy as np
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

__all__ = ['select_region']

def put_chinese_text(image, text, position, font_size=36):
    """
    在图像上添加中文文字
    
    Args:
        image: PIL图像对象
        text: 要添加的中文文本
        position: 文字位置 (x, y)
        font_size: 字体大小
    """
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(image)
    
    # 尝试加载微软雅黑字体，如果失败则使用默认字体
    try:
        # 在Windows系统上尝试加载微软雅黑字体
        font = ImageFont.truetype("msyh.ttc", font_size)
    except:
        try:
            # 尝试其他可能的中文字体文件
            font = ImageFont.truetype("simhei.ttf", font_size)
        except:
            # 如果都失败了，使用默认字体
            font = ImageFont.load_default()
    
    # 在图像上添加文字
    draw.text(position, text, font=font, fill=(0, 255, 0))
    return image

def select_region():
    """
    让用户选择屏幕上的一个区域
    
    Returns:
        tuple: (x, y, width, height) 选择的区域坐标，如果未选择则返回None
    """
    logger.info("正在捕获屏幕截图...")
    
    # 使用Pillow进行截图
    pil_image = ImageGrab.grab()
    # 转换为numpy数组并从RGB转换为BGR以适应OpenCV
    screenshot = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    if screenshot is None:
        logger.error("无法获取屏幕截图")
        return None
    
    # 获取屏幕实际分辨率
    actual_height, actual_width = screenshot.shape[:2]
    logger.info(f"屏幕实际分辨率: {actual_width}x{actual_height}")
    
    scale_factor = 0.5  # 缩放因子，使窗口更容易操作
    
    # 创建缩放版本以便更好地显示
    scaled_width = int(actual_width * scale_factor)
    scaled_height = int(actual_height * scale_factor)
    scaled_screenshot = cv2.resize(screenshot, (scaled_width, scaled_height), interpolation=cv2.INTER_AREA)
    
    # 将OpenCV图像转换为PIL图像以便添加中文文字
    pil_scaled = Image.fromarray(cv2.cvtColor(scaled_screenshot, cv2.COLOR_BGR2RGB))
    
    # 添加中文提示文字
    # 计算文字位置使其居中
    text1 = "拖拽选择区域"
    text2 = "按 'c' 确认, 'r' 重置, 'q' 退出"
    text3 = f"屏幕分辨率: {actual_width}x{actual_height}"
    
    # 创建绘图对象
    draw = ImageDraw.Draw(pil_scaled)
    
    # 尝试加载微软雅黑字体
    try:
        font_large = ImageFont.truetype("msyh.ttc", 36)
        font_small = ImageFont.truetype("msyh.ttc", 24)
    except:
        try:
            font_large = ImageFont.truetype("simhei.ttf", 36)
            font_small = ImageFont.truetype("simhei.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # 计算文字尺寸以居中显示
    text1_bbox = draw.textbbox((0, 0), text1, font=font_large)
    text1_width = text1_bbox[2] - text1_bbox[0]
    text1_x = (scaled_width - text1_width) // 2
    text1_y = 30
    
    text2_bbox = draw.textbbox((0, 0), text2, font=font_small)
    text2_width = text2_bbox[2] - text2_bbox[0]
    text2_x = (scaled_width - text2_width) // 2
    text2_y = 80
    
    text3_bbox = draw.textbbox((0, 0), text3, font=font_small)
    text3_width = text3_bbox[2] - text3_bbox[0]
    text3_x = (scaled_width - text3_width) // 2
    text3_y = 120
    
    # 添加文字到图像
    draw.text((text1_x, text1_y), text1, font=font_large, fill=(0, 255, 0))
    draw.text((text2_x, text2_y), text2, font=font_small, fill=(0, 255, 0))
    draw.text((text3_x, text3_y), text3, font=font_small, fill=(0, 255, 0))
    
    # 转换回OpenCV格式
    scaled_screenshot = cv2.cvtColor(np.array(pil_scaled), cv2.COLOR_RGB2BGR)
    
    # 初始化变量
    start_point = None
    end_point = None
    drawing = False
    region_selected = False
    
    def mouse_callback(event, x, y, flags, param):
        """鼠标回调函数处理绘制事件"""
        nonlocal start_point, end_point, drawing, region_selected
        
        # 将坐标转换回原始图像坐标，使用精确的缩放比例
        x_orig = int(x / scale_factor)
        y_orig = int(y / scale_factor)
        
        # 确保坐标在屏幕范围内
        x_orig = max(0, min(x_orig, actual_width - 1))
        y_orig = max(0, min(y_orig, actual_height - 1))
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # 开始绘制
            start_point = (x_orig, y_orig)
            drawing = True
            region_selected = False

        elif event == cv2.EVENT_MOUSEMOVE:
            # 鼠标移动时更新结束点
            if drawing:
                end_point = (x_orig, y_orig)

        elif event == cv2.EVENT_LBUTTONUP:
            # 结束绘制
            end_point = (x_orig, y_orig)
            drawing = False
            region_selected = True

    # 创建窗口（使用英文名称避免乱码问题）
    window_name = "Region Selector"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    # 设置窗口位置和尺寸
    cv2.resizeWindow(window_name, min(scaled_width, 1200), min(scaled_height, 800))  # 限制最大窗口尺寸
    
    logger.info("请用鼠标拖拽选择一个区域")
    logger.info("按键说明: c - 确认选择, r - 重新选择, q - 退出程序")
    
    display_image = scaled_screenshot.copy()
    
    while True:
        temp_image = display_image.copy()
        
        # 如果正在绘制或已经选择了区域，则显示矩形
        if drawing and start_point and end_point:
            # 转换坐标到缩放图像
            start_scaled = (int(start_point[0] * scale_factor), int(start_point[1] * scale_factor))
            end_scaled = (int(end_point[0] * scale_factor), int(end_point[1] * scale_factor))
            cv2.rectangle(temp_image, start_scaled, end_scaled, (0, 255, 0), 2)
        elif region_selected and start_point and end_point:
            # 转换坐标到缩放图像
            start_scaled = (int(start_point[0] * scale_factor), int(start_point[1] * scale_factor))
            end_scaled = (int(end_point[0] * scale_factor), int(end_point[1] * scale_factor))
            cv2.rectangle(temp_image, start_scaled, end_scaled, (0, 255, 0), 2)
        
        cv2.imshow(window_name, temp_image)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c') and region_selected:
            # 确认选择
            if start_point and end_point:
                # 标准化坐标 (确保start是左上角，end是右下角)
                x1, y1 = start_point
                x2, y2 = end_point
                x_min, x_max = min(x1, x2), max(x1, x2)
                y_min, y_max = min(y1, y2), max(y1, y2)
                
                # 确保区域在屏幕范围内
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(actual_width, x_max)
                y_max = min(actual_height, y_max)
                
                region = (x_min, y_min, x_max - x_min, y_max - y_min)
                logger.info(f"选定区域: x={region[0]}, y={region[1]}, width={region[2]}, height={region[3]}")
                
                # 验证区域是否有效
                if region[2] <= 0 or region[3] <= 0:
                    logger.error("选定区域无效，请重新选择")
                    continue
                
                # 验证区域是否超出屏幕范围
                if x_min < 0 or y_min < 0 or x_max > actual_width or y_max > actual_height:
                    logger.error(f"选定区域超出屏幕范围，请在 0,0 到 {actual_width},{actual_height} 范围内选择")
                    continue
                    
                cv2.destroyWindow(window_name)
                return region
                
        elif key == ord('r'):
            # 重置选择
            start_point = None
            end_point = None
            drawing = False
            region_selected = False
            display_image = scaled_screenshot.copy()
            
        elif key == ord('q'):
            # 退出
            cv2.destroyWindow(window_name)
            return None

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