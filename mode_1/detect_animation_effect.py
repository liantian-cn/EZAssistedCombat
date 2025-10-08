#!/usr/bin/env python3

import dxcam
import cv2
import numpy as np
from PIL import Image
import time
import os
from process_animation_frames import process_animation_frames

# 全局调试开关
DEBUG = True


def main():
    """主函数"""
    if DEBUG:
        # 创建输出目录
        if not os.path.exists("output"):
            os.makedirs("output")
    
    # 创建相机实例
    print("正在创建相机实例...")
    camera = dxcam.create()
    
    if camera is None:
        print("错误: 无法创建相机实例")
        return
    
    try:
        # 抓取5张截图，间隔0.1秒
        print("正在抓取5张截图...")
        frames = []
        
        for i in range(10):
            print(f"抓取第 {i+1} 张截图...")
            # 捕获全屏
            frame = camera.grab()
            
            if frame is None:
                print(f"警告: 第 {i+1} 张截图失败")
                continue
            
            frames.append(frame)
            
            # if DEBUG:
            #     # 保存原始截图
            #     original_image = Image.fromarray(frame)
            #     original_image.save(f"output/screenshot_{i+1}.png")
            
            # 等待0.1秒 (如果需要控制时间间隔)
            # time.sleep(0.1)  # 可能需要导入time模块
        
        if len(frames) == 0:
            print("错误: 没有成功抓取到任何截图")
            return
        
        print(f"成功抓取 {len(frames)} 张截图")
        
        # 使用新的处理函数处理帧
        print("正在处理帧以检测动画效果...")
        detected_boxes = process_animation_frames(frames)
        
        if detected_boxes:
            for i, (x, y, w, h) in enumerate(detected_boxes):
                print(f"找到动画效果方框位置 #{i+1}: x={x}, y={y}, width={w}, height={h}")
            
            if DEBUG:
                # 在最后一帧上绘制所有检测到的方框
                last_frame = frames[-1]
                debug_image = cv2.cvtColor(last_frame, cv2.COLOR_RGB2BGR)
                for (x, y, w, h) in detected_boxes:
                    cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.imwrite("output/detected_boxes.png", debug_image)
                print("检测结果已保存为 output/detected_boxes.png")
        else:
            print("未找到符合条件的动画效果方框")
            
            # 保存最后一帧用于调试
            if DEBUG:
                last_frame = frames[-1]
                debug_image = cv2.cvtColor(last_frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite("output/frame_for_debug.png", debug_image)
                print("帧图像已保存为 output/frame_for_debug.png")
    
    finally:
        # 释放相机资源
        camera.release()
        print("相机资源已释放")


if __name__ == "__main__":
    main()