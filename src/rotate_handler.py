import cv2
import numpy as np
import os
import argparse
from pathlib import Path

def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = (theta - np.pi / 2) * 180 / np.pi
            if abs(angle) < 45:  # Filter outlying angles
                angles.append(angle)

    if len(angles) == 0:
        return image, 0.0

    median_angle = np.median(angles)
    
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated, median_angle

def process_folder(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    files = sorted([f for f in input_path.iterdir() if f.suffix.lower() in extensions])
    
    print(f"Found {len(files)} images in {input_dir}")

    for file_path in files:
        try:
            img = cv2.imread(str(file_path))
            if img is None:
                print(f"Warning: Could not read image {file_path}")
                continue

            rotated_img, angle = deskew(img)
            
            save_name = file_path.name
            save_path = output_path / save_name
            cv2.imwrite(str(save_path), rotated_img)
            
            print(f"Processed {file_path.name}: Start Angle={angle:.2f}, Saved to {save_path}")
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate images in a folder.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing images")
    parser.add_argument("--output_dir", required=True, help="Output directory for rotated images")
    
    args = parser.parse_args()
    
    process_folder(args.input_dir, args.output_dir)
