#!/usr/bin/env python3
"""
EZAssistedCombat 主程序文件
负责协调整个应用程序的运行，包括区域选择、截图、图像分析和结果显示
"""

import threading
import time
import collections
import dxcam
import cv2
# from select_region import select_region
from select_region2 import select_region
from process_animation_frames import process_animation_frames
import pyautogui

# 全局常量定义
TARGET_FPS = 20
BUFFER_SIZE = 7
OUTPUT_RATE = 5

# 全局变量
result_queue = []
result_lock = threading.Lock()
exit_event = threading.Event()


def screenshot_thread(camera, region, buffer):
    """
    截图线程函数
    使用dxcam按照设定的FPS进行截图，并将frame存入环形缓冲区
    """
    try:
        # 启动相机，设置目标FPS
        # dxcam的region参数格式是(left, top, right, bottom)
        camera.start(target_fps=TARGET_FPS, region=region)
        
        while not exit_event.is_set():
            frame = camera.get_latest_frame()
            if frame is not None:
                # 使用collections.deque实现环形缓冲区
                if len(buffer) >= BUFFER_SIZE:
                    buffer.popleft()
                buffer.append(frame)
            # 控制帧率
            # time.sleep(1.0 / TARGET_FPS)
    except Exception as e:
        print(f"截图线程发生错误: {e}")
    finally:
        camera.stop()


def analysis_thread(buffer):
    """
    图像分析线程函数
    从环形缓冲区取出frames进行分析，并将结果存储到线程外变量
    """
    while not exit_event.is_set():
        if len(buffer) >= BUFFER_SIZE:  # 至少需要3帧才能进行分析
            # 获取当前缓冲区中的所有帧进行分析
            frames_to_process = list(buffer)
            detected_boxes = process_animation_frames(frames_to_process)
            
            # 更新全局结果队列
            with result_lock:
                result_queue.clear()
                result_queue.extend(detected_boxes)
        
        # # 控制分析频率
        # time.sleep(1)


def main():
    """主函数"""
    print("欢迎使用EZAssistedCombat!")
    
    # 1. 调用select_region提示用户选定一个区域
    region = select_region()
    if region is None:
        print("未选择区域，程序退出")
        return
    
    # 创建相机实例
    print("正在创建相机实例...")
    camera = dxcam.create()
    if camera is None:
        print("错误: 无法创建相机实例")
        return
    
    # 获取屏幕尺寸
    screen_width = camera.width
    screen_height = camera.height
    
    # 使用选择的区域而不是全屏
    x, y, w, h = region
    print(f"选定区域: x={x}, y={y}, width={w}, height={h}")
    
    # 将(x, y, width, height)格式转换为dxcam需要的(left, top, right, bottom)格式
    # 确保坐标在有效范围内
    left = max(0, min(x, screen_width - 1))
    top = max(0, min(y, screen_height - 1))
    right = max(left + 1, min(x + w, screen_width))
    bottom = max(top + 1, min(y + h, screen_height))
    
    # 为增加容差值，如果上下左右各外扩20像素没超过屏幕边缘，则外扩，或者扩到屏幕边缘
    tolerance = 20
    left = max(0, left - tolerance)
    top = max(0, top - tolerance)
    right = min(screen_width, right + tolerance)
    bottom = min(screen_height, bottom + tolerance)
    
    # dxcam的region参数格式是[left, top, right, bottom]，其中right和bottom是不包含的边界
    dxcam_region = (left, top, right, bottom)
    print(f"dxcam区域参数: {dxcam_region}")
    
    # 创建环形缓冲区
    frame_buffer = collections.deque(maxlen=BUFFER_SIZE)
    
    # 创建并启动线程
    print("启动截图线程...")
    shot_thread = threading.Thread(target=screenshot_thread, args=(camera, dxcam_region, frame_buffer))
    shot_thread.daemon = True
    shot_thread.start()
    
    print("启动图像分析线程...")
    analysis_thread_obj = threading.Thread(target=analysis_thread, args=(frame_buffer,))
    analysis_thread_obj.daemon = True
    analysis_thread_obj.start()
    
    # 主线程: 每秒最多OUTPUT_RATE次输出结果
    last_output_time = 0
    output_interval = 1.0 / OUTPUT_RATE
    
    print("开始监控，按Ctrl+C退出程序")
    try:
        while True:
            current_time = time.time()
            if current_time - last_output_time >= output_interval:
                with result_lock:
                    if result_queue:
                        # print(f"[{time.strftime('%H:%M:%S')}] 检测到 {len(result_queue)} 个动画效果方框:")
                        # for i, (bx, by, bw, bh) in enumerate(result_queue):
                        #     # 计算真实屏幕坐标，需要考虑容差值
                        #     real_x = left + bx
                        #     real_y = top + by
                        #     print(f"  方框 #{i+1}: 屏幕坐标({real_x}, {real_y}), 尺寸({bw}x{bh})")
                        bx, by, bw, bh = result_queue[0]
                        real_x = left + bx
                        real_y = top + by
                        # print(f"屏幕坐标({real_x}, {real_y}), 尺寸({bw}x{bh})")
                        
                        # 移动鼠标到矩形中心并点击
                        center_x = real_x + bw // 2
                        center_y = real_y + bh // 2
                        pyautogui.click(center_x, center_y)
                        print(f"已在坐标 ({center_x}, {center_y}) 处点击")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] 未检测到动画效果方框")
                
                last_output_time = current_time

            
    except KeyboardInterrupt:
        print("\n正在退出程序...")
        exit_event.set()
        
        # 等待线程结束
        shot_thread.join(timeout=1)
        analysis_thread_obj.join(timeout=1)
        
        # 停止相机
        camera.stop()
        print("程序已退出")


if __name__ == "__main__":
    main()