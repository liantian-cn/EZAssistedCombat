#!/usr/bin/env python3

import cv2
import numpy as np
import os
from datetime import datetime
from typing import List, Tuple

DEBUG = False

# 尺寸参数
MIN_WIDTH = 48
MAX_WIDTH = 128
MIN_HEIGHT = 48
MAX_HEIGHT = 128
BORDER_MIN_WIDTH = 1
BORDER_MAX_WIDTH = 2

# 颜色范围参数 (BGR格式)
LOWER_BOUND = np.array([190, 190, 0])
UPPER_BOUND = np.array([255, 255, 100])


def extract_target_pixels_from_frames(frames):
    """
    从多个帧中提取目标颜色像素
    
    Args:
        frames: 多个图像帧的列表，每个帧应该是numpy数组格式
        
    Returns:
        掩码帧的列表
    """
    masks = []
    for frame in frames:
        # 转换颜色空间从RGB到BGR以适应OpenCV
        bgr_image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # 创建掩码
        mask = cv2.inRange(bgr_image, LOWER_BOUND, UPPER_BOUND)
        masks.append(mask)
    
    return masks


def merge_frames(frames):
    """
    合并多个帧
    
    Args:
        frames: 掩码帧的列表
        
    Returns:
        合并后的图像
    """
    if not frames:
        return None
    
    # 初始化合并图像为第一个帧
    merged = frames[0].copy()
    
    # 对所有帧进行按位或操作
    for frame in frames[1:]:
        merged = cv2.bitwise_or(merged, frame)

    return merged


def extract_rectangular_contours(
    binary_image: np.ndarray,
    min_area: float = 100.0,
    max_area: float = float('inf'),
    aspect_ratio_range: Tuple[float, float] = (1.0, 4.0),
    epsilon_factor: float = 0.02,
    min_solidity: float = 0.8
) -> List[np.ndarray]:
    """
    从二值图像中提取符合矩形特征的轮廓。

    参数:
        binary_image: 单通道二值图 (uint8)
        min_area: 最小面积阈值
        max_area: 最大面积阈值
        aspect_ratio_range: 宽高比范围 (min, max)，自动取绝对值比
        epsilon_factor: 多边形逼近系数
        min_solidity: 最小实度（面积 / 凸包面积）

    返回:
        符合条件的矩形轮廓列表
    """
    if binary_image.dtype != np.uint8 or len(binary_image.shape) != 2:
        raise ValueError("输入必须是单通道8位图像")

    contours, _ = cv2.findContours(
        binary_image.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    rectangles = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area or area > max_area:
            continue

        # 多边形逼近
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon_factor * peri, True)
        if len(approx) != 4:
            continue

        # 宽高比检查
        x, y, w, h = cv2.boundingRect(cnt)
        ar = max(w, h) / min(w, h)
        if not (aspect_ratio_range[0] <= ar <= aspect_ratio_range[1]):
            continue

        # 实度检查（可选）
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        if solidity < min_solidity:
            continue

        rectangles.append(cnt)

    return rectangles


def detect_contours_with_criteria(image):
    """
    检测符合特定条件的轮廓
    
    Args:
        image: 输入图像
        
    Returns:
        包含所有符合条件的轮廓坐标的列表，每个元素是(x, y, w, h)元组
    """
    # 使用改进的矩形检测函数
    rectangles = extract_rectangular_contours(
        image,
        min_area=MIN_WIDTH * MIN_HEIGHT,  # 最小面积
        max_area=MAX_WIDTH * MAX_HEIGHT,  # 最大面积
        aspect_ratio_range=(0.8, 1.2),  # 更严格的正方形要求 (误差20%以内)
        epsilon_factor=0.02,  # 多边形逼近系数
        min_solidity=0.7  # 最小实度
    )
    
    detected_boxes = []
    failed_contours = []
    
    for contour in rectangles:
        x, y, w, h = cv2.boundingRect(contour)
        
        # 检查尺寸是否符合要求

        if MIN_WIDTH <= w <= MAX_WIDTH and MIN_HEIGHT <= h <= MAX_HEIGHT:
            detected_boxes.append((x, y, w, h))
            # contour_area = cv2.contourArea(contour)
            # outer_area = w * h
            # inner_area_min = (w - BORDER_MAX_WIDTH * 2) * (h - BORDER_MAX_WIDTH * 2)
            # inner_area_max = (w - BORDER_MIN_WIDTH * 2) * (h - BORDER_MIN_WIDTH * 2)
            # inner_empty_area = outer_area - contour_area
            #
            # # 检查内部空白区域是否符合边框特征
            # if inner_area_min * 0.8 <= inner_empty_area <= inner_area_max * 1.2:
            #     detected_boxes.append((x, y, w, h))
            # elif DEBUG:
            #     # 如果在调试模式下，记录不满足内部区域条件的轮廓
            #     print(f"内部区域不符合要求：{x}, {y}, {w}, {h}")
            #     failed_contours.append(contour)
        elif DEBUG:
            print(f"尺寸不符合要求：{x}, {y}, {w}, {h}")
            # 如果在调试模式下，记录不满足尺寸条件的轮廓
            failed_contours.append(contour)
    
    # 如果在调试模式下，将输入图像与检测结果叠加保存
    if DEBUG:
        # 确保output目录存在
        if not os.path.exists("output"):
            os.makedirs("output")
        
        # 创建彩色图像用于绘制
        debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # 绘制满足条件的轮廓（红色）
        for (x, y, w, h) in detected_boxes:
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        # 绘制不满足条件的轮廓（紫色）
        for contour in failed_contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 255), 2)
        
        # 生成带时间戳的文件名（精确到秒）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/contours_debug_{timestamp}.png"
        
        # 保存图像
        cv2.imwrite(filename, debug_image)
        print(f"轮廓检测调试图像已保存为 {filename}")
    
    return detected_boxes


def process_animation_frames(frames):
    """
    主函数：处理多个动画帧并返回符合条件的轮廓坐标
    
    Args:
        frames: 多个图像帧的列表，每个帧应该是numpy数组格式
        
    Returns:
        包含所有符合条件的轮廓坐标的列表，每个元素是(x, y, w, h)元组
    """
    # 从帧中提取目标像素
    masks = extract_target_pixels_from_frames(frames)
    
    # 合并所有掩码图像
    merged_mask = merge_frames(masks)
    
    if merged_mask is None:
        return []
    
    # 检测符合标准的轮廓
    detected_boxes = detect_contours_with_criteria(merged_mask)
    
    return detected_boxes


if __name__ == "__main__":
    # 这里只是示例用法说明，实际使用时不会执行截图
    print("这是处理动画帧的模块")
    print("请调用 process_animation_frames(frames) 函数，传入帧列表")
    print("函数将返回符合条件的轮廓坐标列表 [(x, y, w, h), ...]")