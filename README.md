# Book OCR Pipeline

A comprehensive OCR pipeline that processes book pages using a combination of traditional Computer Vision (PaddleOCR) and Large Language Models (LLM) for high-quality text extraction and formatting.

## Features

- **Automated Processing**: Full pipeline from image rotation to final Markdown generation.
- **Hybrid Approach**:
  - **Vision Stage**: Uses PaddleOCR for layout analysis (detecting crops, tables, figures).
  - **LLM Stage**: Uses Multimodal LLMs (e.g., Qwen-VL, DeepSeek) for accurate text recognition and formatting.
- **Markdown Output**: Generates clean, formatted Markdown with support for headers, lists, code blocks, and LaTeX formulas.
- **Modular Design**: Separate handlers for each stage of processing.

## Project Structure

```
.
├── input/                  # Place input image folders here
├── output/                 # Generated results
├── src/                    # Source code for pipeline stages
│   ├── rotate_handler.py   # Step 1: Image rotation & deskewing
│   ├── segment_handler.py  # Step 2: Layout analysis (PaddleOCR)
│   ├── padding_handler.py  # Step 3: Image padding
│   ├── llm_handler.py      # Step 4: LLM-based recognition
│   └── merger.py          # Step 5: Merge fragments into final MD
├── env_vision/             # Virtual environment for Vision tasks
├── env_llm/                # Virtual environment for LLM tasks
├── pipeline_run.py         # Main entry point script
└── .env                    # Environment configuration (API keys)
```

## Prerequisites

The pipeline relies on two separate Python environments to manage dependencies (Vision vs LLM):

1. **env_vision**: Contains `paddlepaddle`, `paddleocr`, `opencv-python`.
2. **env_llm**: Contains `openai`, `python-dotenv`.

Ensure these environments are created in the root directory as `env_vision` and `env_llm`.

### Configuration (.env)

Create a `.env` file in the root directory with your LLM API credentials:

```ini
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.siliconflow.cn/v1  # or your provider's URL
```

## Usage

1. **Prepare Input**:
    Create a folder inside `input/` (e.g., `my_book`) and place your page images (jpg, png) inside it.

    ```
    input/
    └── my_book/
        ├── page_001.jpg
        ├── page_002.jpg
        └── ...
    ```

2. **Run Pipeline**:
    Execute the main script with the folder name:

    ```bash
    # Typically run from your base python or system python
    python pipeline_run.py my_book
    ```

    The script will automatically switch between `env_vision` and `env_llm` for different steps.

3. **Check Output**:
    Results will be in `output/my_book/`.
    - Intermediate steps: `step1_rotated`, `step2_crops`, `step3_md_fragments`
    - **Final Result**: `output/my_book/my_book.md`

## Pipeline Steps

1. **Rotation**: Corrects orientation of scanned pages.
2. **Segmentation**: Detects regions (Text, Title, Table, Figure) using PaddleOCR.
3. **Padding**: Adjusts image dimensions for optimal LLM processing.
4. **LLM Recognition**: Sends image crops to the VLM for text extraction and formatting.
5. **Merge**: Combines all fragments into a single coherent Markdown document.

## License

[License Information]
