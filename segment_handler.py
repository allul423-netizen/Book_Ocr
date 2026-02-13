import os
import cv2
import argparse
from pathlib import Path
from paddleocr import PPStructure

def main(input_dir, output_base_dir):
    # Initialize the layout analysis engine
    # Using v2 API as per plan/reference
    # Explicitly disable GPU and MKLDNN to avoid OneDNN errors
    layout_engine = PPStructure(show_log=True, image_orientation=False, use_gpu=False, enable_mkldnn=False)


    input_path = Path(input_dir)
    # The output for step 2 should be inside the project output folder structure
    # The plan says: output/[folder]/step2_crops/
    # Let's assume input_dir is input/test, so output_base_dir is output/test
    
    output_crops_dir = Path(output_base_dir) / "step2_crops"
    output_crops_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = Path(output_base_dir) / "processing_log.txt"
    
    extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    files = sorted([f for f in input_path.iterdir() if f.suffix.lower() in extensions])
    
    print(f"Starting layout analysis on {len(files)} files in {input_dir}")
    
    total_crops = 0
    
    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"Processing Log - {input_dir}\n")
        log.write("="*40 + "\n")

        for file_index, file_path in enumerate(files):
            try:
                print(f"Processing {file_path.name}...")
                img = cv2.imread(str(file_path))
                if img is None:
                    msg = f"Error: Could not read image {file_path}\n"
                    print(msg.strip())
                    log.write(msg)
                    continue

                result = layout_engine(img)
                
                # Filter logic: only keep title, text, figure, table
                valid_types = {'title', 'text', 'figure', 'table'}
                
                file_crop_count = 0
                # Sort regions by Y-coordinate (top) to ensure top-to-bottom order
                result.sort(key=lambda x: x['bbox'][1])

                for i, region in enumerate(result):
                    category = region['type']
                    if category not in valid_types:
                        continue
                    
                    crop_img = region['img']
                    
                    # Naming: crop_{original_filename_stem}_{index}_{type}.png
                    # Plan said: crop_{index}_{type}.png but we need to distinguish source files if we process multiple?
                    # Plan said: "按照 crop_{index}_{type}.png 命名，存入 step2_crops/"
                    # It implies per-page processing or unique global index. 
                    # Let's include the original filename stem to be safe and avoid collisions if multiple input images.
                    # Or maybe the intention is to have a folder per input file? 
                    # "将校正后的图片存入 output/[folder]/step1_rotated/" -> It seems one folder per project/book.
                    # Let's follow: crop_{original_file_index}_{region_index}_{type}.png to be safe and sortable.
                    
                    file_name = f"crop_{file_index:03d}_{i:03d}_{category}.png"
                    save_path = output_crops_dir / file_name
                    
                    cv2.imwrite(str(save_path), crop_img)
                    file_crop_count += 1
                    total_crops += 1
                
                log.write(f"{file_path.name}: {file_crop_count} crops extracted.\n")
                print(f"  -> Extracted {file_crop_count} valid crops.")

            except Exception as e:
                msg = f"Error processing {file_path.name}: {str(e)}\n"
                print(msg.strip())
                log.write(msg)
        
        log.write("="*40 + "\n")
        log.write(f"Total crops extracted: {total_crops}\n")

    print(f"Layout analysis complete. Log saved to {log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform layout analysis on images.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing rotated images")
    parser.add_argument("--output_dir", required=True, help="Base output directory for the current task")
    
    args = parser.parse_args()
    
    main(args.input_dir, args.output_dir)
