import sys
import os
import subprocess
import argparse
from pathlib import Path

# Paths to Python executables in virtual environments
ENV_VISION_PYTHON = Path("env_vision/Scripts/python.exe")
ENV_LLM_PYTHON = Path("env_llm/Scripts/python.exe")

def run_step(python_exe, script_path, args, description):
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"Running: {python_exe} {script_path} {' '.join(args)}")
    print(f"{'='*60}\n")
    
    cmd = [str(python_exe), str(script_path)] + args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing step '{description}': {e}")
        sys.exit(1)

def main(folder_name):
    # Setup paths
    base_input_dir = (Path("input") / folder_name).resolve()
    base_output_dir = (Path("output") / folder_name).resolve()
    
    if not base_input_dir.exists():
        print(f"Error: Input directory {base_input_dir} does not exist.")
        sys.exit(1)
        
    base_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Rotate (Vision Env)
    # Output to output/[folder]/step1_rotated
    step1_output = base_output_dir / "step1_rotated"
    run_step(
        ENV_VISION_PYTHON, 
        "rotate_handler.py", 
        ["--input_dir", str(base_input_dir), "--output_dir", str(step1_output)],
        "1. Image Rotation & Deskewing"
    )
    
    # 2. Segment/Layout Analysis (Vision Env)
    # Output to output/[folder]/step2_crops (Created by segment_handler inside output_dir)
    # Note segment_handler expects output_base_dir and creates step2_crops inside it.
    run_step(
        ENV_VISION_PYTHON, 
        "segment_handler.py", 
        ["--input_dir", str(step1_output), "--output_dir", str(base_output_dir)],
        "2. Layout Analysis & Segmentation"
    )
    
    step2_crops = base_output_dir / "step2_crops"
    
    # 3. Padding (LLM Env)
    # Output to output/[folder]/step2_padded
    step2_padded = base_output_dir / "step2_padded"
    run_step(
        ENV_LLM_PYTHON,
        "padding_handler.py",
        ["--input_dir", str(step2_crops), "--output_dir", str(step2_padded)],
        "3. Image Padding (56px Constraint)"
    )
    
    # 4. LLM Recognition (LLM Env)
    # Output to output/[folder]/step3_md_fragments
    step3_output = base_output_dir / "step3_md_fragments"
    run_step(
        ENV_LLM_PYTHON,
        "llm_handler.py",
        ["--input_dir", str(step2_padded), "--output_dir", str(step3_output)],
        "4. LLM Content Recognition"
    )
    
    # 5. Merge (LLM Env)
    # Output to output/[folder]/final_result.md
    final_output = base_output_dir / "final_result.md"
    run_step(
        ENV_LLM_PYTHON,
        "merger.py",
        ["--input_dir", str(step3_output), "--output_file", str(final_output)],
        "5. Final Document Merging"
    )
    
    print(f"\nPipeline completed successfully!")
    print(f"Final output: {final_output.absolute()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full OCR pipeline.")
    parser.add_argument("folder_name", help="Name of the folder inside 'input/' to process")
    
    args = parser.parse_args()
    
    main(args.folder_name)
