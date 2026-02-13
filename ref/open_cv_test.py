import cv2
import numpy as np

# 读取图像


img = cv2.imread(r'D:\Antigravity\Deepseek_OCR\testdata\pic\3_07.jpg')


def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = (theta - np.pi / 2) * 180 / np.pi
            if abs(angle) < 45:  # 过滤异常角度
                angles.append(angle)

    if len(angles) == 0:
        print("未检测到明显直线，返回原图")
        return image

    median_angle = np.median(angles)
    print(f"估计的倾斜角度为: {median_angle:.2f} 度")

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated


# 调用函数去倾斜
corrected_img = deskew(img)

# 保存处理后的图像
save_path = r'D:\Antigravity\Deepseek_OCR\pic_rotated.jpg'
success = cv2.imwrite(save_path, corrected_img)

if success:
    print(f"去倾斜图像已保存至: {save_path}")
else:
    print("图像保存失败，请检查路径或权限")