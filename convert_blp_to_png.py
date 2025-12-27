#!/usr/bin/env python3
"""
BLP to PNG Converter

This script converts BLP format images to PNG format using Pillow library.
BLP is a texture format used in games like World of Warcraft.
"""

import os
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)

def convert_blp_to_png(input_dir="icons", output_dir="icons"):
    """
    Convert all BLP files in the input directory to PNG format.
    
    Args:
        input_dir (str): Directory containing BLP files
        output_dir (str): Directory to save PNG files
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        return
    
    # Counter for converted files
    converted_count = 0
    
    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.blp'):
            blp_path = os.path.join(input_dir, filename)
            png_filename = os.path.splitext(filename)[0] + '.png'
            png_path = os.path.join(output_dir, png_filename)
            
            try:
                # Open BLP file with Pillow
                with Image.open(blp_path) as img:
                    # Convert to RGBA if needed
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Save as PNG
                    img.save(png_path, 'PNG')
                    logger.info(f"Converted: {filename} -> {png_filename}")
                    converted_count += 1
                    
                    # Remove original BLP file after successful conversion
                    os.remove(blp_path)
                    logger.info(f"Removed original file: {filename}")
                    
            except Exception as e:
                logger.error(f"Failed to convert {filename}: {str(e)}")
    
    logger.info(f"Conversion completed. Total converted files: {converted_count}")

if __name__ == "__main__":
    convert_blp_to_png()