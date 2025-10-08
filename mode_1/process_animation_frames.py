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

    for contour in rectangles:
        x, y, w, h = cv2.boundingRect(contour)
        
        # 检查尺寸是否符合要求

        if MIN_WIDTH <= w <= MAX_WIDTH and MIN_HEIGHT <= h <= MAX_HEIGHT:
            detected_boxes.append((x, y, w, h))

    
    return detected_boxes


def save_debug_images(frames, merged_mask, detected_boxes):
    """
    保存调试图片
    
    Args:
        frames: 原始帧列表
        merged_mask: 合并后的掩码图像
        detected_boxes: 检测到的边界框列表
    """
    if not DEBUG:
        return
    
    # 创建output目录
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成时间戳
    timestamp = str(int(datetime.now().timestamp() * 1000))
    
    # 创建要垂直叠加的图像列表
    debug_images = []
    
    # 1. 将frames的最后一帧生成一份"原图"
    if frames:
        # 注意：frames中的图像是RGB格式，需要转换为BGR格式以便OpenCV正确处理
        original_image = cv2.cvtColor(frames[-1], cv2.COLOR_RGB2BGR)
        debug_images.append(original_image)
    
    # 2. merged_mask生成一份"过程1图"
    if merged_mask is not None:
        process1_image = cv2.cvtColor(merged_mask, cv2.COLOR_GRAY2BGR)
        debug_images.append(process1_image)
    
    # 3. detected_boxes绘制在merged_mask生成过程2图
    if merged_mask is not None:
        process2_image = cv2.cvtColor(merged_mask, cv2.COLOR_GRAY2BGR)
        for (x, y, w, h) in detected_boxes:
            cv2.rectangle(process2_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        debug_images.append(process2_image)
    
    # 4. detected_boxes绘制在最后一帧生成结果图
    if frames:
        # 注意：frames中的图像是RGB格式，需要转换为BGR格式以便OpenCV正确处理
        result_image = cv2.cvtColor(frames[-1], cv2.COLOR_RGB2BGR)
        for (x, y, w, h) in detected_boxes:
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        debug_images.append(result_image)
    
    # 垂直叠加所有图像
    if debug_images:
        # 确保所有图像具有相同的宽度
        max_width = max(img.shape[1] for img in debug_images)
        resized_images = []
        for img in debug_images:
            if len(img.shape) == 2:  # 灰度图转为彩色图
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            # 调整图像大小以匹配最大宽度
            height, width = img.shape[:2]
            if width != max_width:
                # 保持宽高比
                scale = max_width / width
                new_height = int(height * scale)
                img = cv2.resize(img, (max_width, new_height))
            resized_images.append(img)
        
        # 垂直叠加图像
        combined_image = cv2.vconcat(resized_images)
        
        # 保存图像
        output_path = os.path.join(output_dir, f"debug_{timestamp}.png")
        cv2.imwrite(output_path, combined_image)


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
    
    # 保存调试图片
    if DEBUG:
        save_debug_images(frames, merged_mask, detected_boxes)
    
    return detected_boxes


if __name__ == "__main__":
    # 这里只是示例用法说明，实际使用时不会执行截图
    print("这是处理动画帧的模块")
    print("请调用 process_animation_frames(frames) 函数，传入帧列表")
    print("函数将返回符合条件的轮廓坐标列表 [(x, y, w, h), ...]")