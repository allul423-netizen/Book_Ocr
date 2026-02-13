import os
import argparse
from pathlib import Path
from PIL import Image, ImageOps

def pad_image(image_path, min_size=56):
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            if w >= min_size and h >= min_size:
                return False, None
            
            # Calculate padding
            delta_w = max(0, min_size - w)
            delta_h = max(0, min_size - h)
            
            padding = (
                delta_w // 2, 
                delta_h // 2, 
                delta_w - (delta_w // 2), 
                delta_h - (delta_h // 2)
            )
            
            # Pad with white color (255, 255, 255)
            # Handle different modes (e.g. RGBA vs RGB)
            if img.mode == 'RGBA':
                fill = (255, 255, 255, 255)
            else:
                fill = (255, 255, 255)
                
            new_img = ImageOps.expand(img, padding, fill=fill)
            return True, new_img.convert('RGB') # Convert to RGB to ensure compatibility
            
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False, None

def main(input_dir, output_dir=None):
    input_path = Path(input_dir)
    # If no output_dir specified, overwrite (or use a sensible default if we want safety)
    # But for "padding handler", it implies preparing the images. 
    # Let's default to overwriting if output_dir is same or None, 
    # but the plan implies a flow. Let's start with in-place or designated output.
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path

    extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    files = sorted([f for f in input_path.iterdir() if f.suffix.lower() in extensions])
    
    print(f"Checking {len(files)} images for padding requirements in {input_dir}")
    
    padded_count = 0
    
    for file_path in files:
        needs_padding, padded_img = pad_image(file_path)
        
        save_path = output_path / file_path.name
        
        if needs_padding:
            print(f"Padding applied to {file_path.name}")
            padded_img.save(save_path)
            padded_count += 1
        elif output_dir and output_dir != input_dir:
            # If we are saving to a new directory, we must copy the original file even if not padded
            import shutil
            shutil.copy2(file_path, save_path)
            
    print(f"Padding complete. {padded_count} images were padded.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pad images to a minimum size.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing cropped images")
    parser.add_argument("--output_dir", help="Output directory (optional, default: overwrite in place or copy)")
    
    args = parser.parse_args()
    
    main(args.input_dir, args.output_dir)
