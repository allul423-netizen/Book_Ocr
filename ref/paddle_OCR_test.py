import os
import cv2
from paddleocr import PPStructure

# 1. 初始化版面分析引擎
# 注意：之前我们确认过，v2 API 比较稳定
layout_engine = PPStructure(show_log=True, image_orientation=False)

# 2. 传入图片
img_path = r'D:\Antigravity\Deepseek_OCR\pic_rotated.jpg'
img = cv2.imread(img_path)

if img is None:
    raise ValueError(f"无法读取图片: {img_path}")

# 3. 进行预测
print("正在进行版面分析...")
result = layout_engine(img)

# 4. 设置保存切片的文件夹
output_dir = './output_crops'  # 切片保存路径
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"已创建输出文件夹: {output_dir}")

# 5. 根据类别分别处理并保存图片
# 使用 enumerate 获取序号 i，防止重名
for i, region in enumerate(result):
    category = region['type']  # 类别 (text, title, figure, table 等)
    bbox = region['bbox']  # 坐标
    res = region.get('res')  # OCR 识别结果
    crop_img = region['img']  # 裁剪好的子图

    # --- 核心修改：构建文件名并保存 ---
    # 文件名格式：序号_类别.jpg (例如: 0_title.jpg, 1_text.jpg)
    file_name = f"{i}_{category}.jpg"
    save_path = os.path.join(output_dir, file_name)

    # 保存图片
    cv2.imwrite(save_path, crop_img)
    print(f"[{i}] 检测到 {category}，已保存至: {save_path}")

    # --- 下面是原本的打印逻辑 ---
    if category == 'table':
        print("    -> [表格] 建议后续进行 Excel 导出")

    elif category in ['title', 'text', 'header']:
        # 如果有文字识别结果，简单打印前20个字符示意
        if res:
            text_content = "".join([line['text'] for line in res])
            print(f"    -> [文本预览]: {text_content[:30]}...")

print(f"\n所有切片处理完成，请查看文件夹: {os.path.abspath(output_dir)}")