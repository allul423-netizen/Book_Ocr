import sys
import os

try:
    import cv2
    print(f"OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"Error importing cv2: {e}")

try:
    import numpy as np
    print(f"Numpy version: {np.__version__}")
except ImportError as e:
    print(f"Error importing numpy: {e}")

try:
    import paddle
    print(f"PaddlePaddle version: {paddle.__version__}")
    print(f"Paddle device: {paddle.device.get_device()}")
except ImportError as e:
    print(f"Error importing paddle: {e}")

try:
    from paddleocr import PPStructure
    print("PaddleOCR imported successfully")
except ImportError as e:
    print(f"Error importing paddleocr: {e}")

print("Vision Environment Verification Complete.")
