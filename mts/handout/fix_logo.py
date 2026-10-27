#!/usr/bin/env python3
"""Fix the logo flame alignment by shifting flame left by 12 pixels.

The flame was centered at x=413, but should be centered at x=401
to align with the intersection at y=270.
"""

from pathlib import Path
import cv2
import numpy as np

def fix_logo(input_path: str, output_path: str) -> None:
    """Fix the logo by shifting the flame area left by 12 pixels."""
    # Load source
    src = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if src is None:
        raise ValueError(f"Failed to load image: {input_path}")
    
    bgr = src[:, :, :3]
    alpha = src[:, :, 3]
    h, w = src.shape[:2]
    
    # Create result as copy of original
    result = src.copy()
    
    # Flame area to shift (y=180-250)
    y_flame_start, y_flame_end = 180, 250
    offset = 18  # pixels to shift left
    
    # Clear flame pixels at original positions
    for y in range(y_flame_start, y_flame_end + 1):
        for x in range(w):
            if alpha[y, x] > 50:  # Flame pixel
                result[y, x, 3] = 0  # Make transparent
                result[y, x, :3] = [0, 0, 0]
    
    # Copy flame pixels to new positions (shifted left by offset)
    for y in range(y_flame_start, y_flame_end + 1):
        for x in range(w):
            if alpha[y, x] > 50:
                new_x = x - offset
                if 0 <= new_x < w:
                    result[y, new_x, :] = src[y, x, :]
    
    # Add bottom padding (788 - 710 = 78 rows)
    h_full, w_full = 788, 834
    result_padded = np.zeros((h_full, w_full, 4), dtype=np.uint8)
    result_padded[:h, :] = result
    
    # Save result
    cv2.imwrite(output_path, result_padded)
    print(f"Saved: {output_path}")

def verify_alignment(input_path: str) -> None:
    """Verify the flame alignment in the generated image."""
    from PIL import Image
    
    img = Image.open(input_path)
    px = img.load()
    
    # Check flame alignment
    flame_centers = []
    for y in range(180, 251):
        row = [px[x, y][3] for x in range(834)]
        non_zero = [i for i, a in enumerate(row) if a > 50]
        if len(non_zero) > 10:
            center = non_zero[0] + (non_zero[-1] - non_zero[0]) // 2
            flame_centers.append((y, center))
    
    flame_avg = sum([c[1] for c in flame_centers]) // len(flame_centers)
    
    # Check intersection center at y=270
    row_int = [px[x, 270][3] for x in range(834)]
    int_non_zero = [i for i, a in enumerate(row_int) if a > 200]
    int_center = int_non_zero[0] + (int_non_zero[-1] - int_non_zero[0]) // 2
    
    # Check fork edges
    left_edge = [px[0, y][3] for y in range(375, 387)]
    right_edge = [px[833, y][3] for y in range(363, 389)]
    
    print(f"File: {img.size}")
    print(f"Flame center (avg): x={flame_avg}")
    print(f"Intersection center: x={int_center}")
    print(f"Offset: {flame_avg - int_center} pixels")
    print(f"Left edge (x=0) preserved: {left_edge == [1, 2, 3, 6, 8, 10, 10, 12, 13, 9, 5, 2]}")
    print(f"Right edge (x=833) preserved: {right_edge == [2, 4, 8, 12, 18, 27, 34, 42, 46, 54, 61, 68, 70, 73, 77, 80, 74, 63, 51, 39, 31, 22, 13, 6, 2, 1]}")

if __name__ == "__main__":
    input_path = "/home/matt/projects/moldvan.com/mts/brand-kit/logos/primary_logo_lockup.png"
    output_path = "/home/matt/projects/moldvan.com/mts/handout/assets/generated/logo_lockup_v2.png"
    
    fix_logo(input_path, output_path)
    verify_alignment(output_path)
