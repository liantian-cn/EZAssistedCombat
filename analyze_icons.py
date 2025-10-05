#!/usr/bin/env python3
"""
分析 icons_opaque 目录下所有 PNG 图标文件的颜色信息
仅统计完全不透明的像素(alpha=255)
"""

import os
from PIL import Image
from collections import defaultdict

def analyze_icon_colors(icon_dir):
    """
    分析图标目录中所有PNG文件的颜色分布
    
    Args:
        icon_dir (str): 包含PNG图标的目录路径
    """
    # 获取所有PNG文件
    png_files = [f for f in os.listdir(icon_dir) if f.lower().endswith('.png')]
    
    if not png_files:
        print(f"在目录 {icon_dir} 中未找到PNG文件")
        return
    
    print(f"找到 {len(png_files)} 个PNG文件")
    print("=" * 50)
    
    # 用于统计所有文件中颜色出现的次数
    total_color_count = defaultdict(int)
    
    # 分析每个PNG文件
    for png_file in sorted(png_files):
        file_path = os.path.join(icon_dir, png_file)
        print(f"\n分析文件: {png_file}")
        print("-" * 30)
        
        try:
            # 打开PNG图像
            with Image.open(file_path) as img:
                # 转换为RGBA模式以确保有alpha通道
                img = img.convert('RGBA')
                
                # 获取图像尺寸
                width, height = img.size
                print(f"图像尺寸: {width}x{height}")
                
                # 统计当前图像的颜色
                color_count = defaultdict(int)
                
                # 遍历每个像素
                for y in range(height):
                    for x in range(width):
                        # 获取像素的RGBA值
                        r, g, b, a = img.getpixel((x, y))
                        
                        # 只统计完全不透明的像素(alpha=255)
                        if a == 255:
                            rgb = (r, g, b)
                            color_count[rgb] += 1
                            total_color_count[rgb] += 1
                
                # 打印当前图像的颜色信息，按出现次数排序（从大到小）
                if color_count:
                    print(f"不透明像素数: {sum(color_count.values())}")
                    print("RGB颜色值 (按出现次数排序):")
                    # 按出现次数从大到小排序
                    sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
                    for rgb, count in sorted_colors:
                        print(f"  RGB{rgb}: {count} 像素")
                else:
                    print("未找到完全不透明的像素")
                    
        except Exception as e:
            print(f"处理文件 {png_file} 时出错: {e}")
    
    # 打印所有文件的总颜色统计，按出现次数排序（从大到小）
    print("\n" + "=" * 50)
    print("所有文件的颜色统计 (按出现次数排序):")
    print("=" * 50)
    if total_color_count:
        print("RGB颜色值:")
        # 按出现次数从大到小排序
        sorted_total_colors = sorted(total_color_count.items(), key=lambda x: x[1], reverse=True)
        for rgb, count in sorted_total_colors:
            print(f"  RGB{rgb}: {count} 像素")
        
        # 计算并输出所有颜色计数的总和
        total_pixels = sum(total_color_count.values())
        print(f"\n所有文件不透明像素总数: {total_pixels}")
    else:
        print("未找到任何完全不透明的像素")

def main():
    """主函数"""
    # 定义图标目录路径
    icon_dir = "icons_opaque"
    
    # 检查目录是否存在
    if not os.path.exists(icon_dir):
        print(f"错误: 目录 '{icon_dir}' 不存在")
        return
    
    if not os.path.isdir(icon_dir):
        print(f"错误: '{icon_dir}' 不是一个目录")
        return
    
    # 分析图标颜色
    analyze_icon_colors(icon_dir)

if __name__ == "__main__":
    main()