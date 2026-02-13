import os
import base64
import yaml
import logging
import time
from datetime import datetime
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== Logging Configuration ====================
def setup_logger(base_dir):
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Simple fixed name for the latest test, or timestamped
    log_file = log_dir / f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logger = logging.getLogger("DeepSeek-OCR")
    logger.setLevel(logging.INFO)
    
    # Format: Time - Level - Message
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(formatter)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

# ==================== Configuration Loading ====================
def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        return {
            "model_id": "deepseek-ai/DeepSeek-OCR",
            "max_tokens": 2048,
            "prompt": "请帮我识别图片中的文字，。"
        }
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_images(directory_path, base_output_dir, test_file=None):
    pic_dir = Path(directory_path)
    base_res_dir = Path(base_output_dir)
    
    # Setup Logger
    logger = setup_logger(Path(__file__).parent)
    logger.info("=" * 60)
    logger.info("Starting OCR Task" + (" (TEST MODE)" if test_file else ""))
    
    # Load config
    config = load_config()
    model_id = config.get("model_id", "deepseek-ai/DeepSeek-OCR")
    max_tokens = config.get("max_tokens", 2048)
    prompt_text = config.get("prompt", "# Role\n你是一个拥有高级排版理解能力的专业 OCR（光学字符识别）引擎。你的核心任务是高保真地从附图中提取文字，并将其转换为清晰、连贯的 Markdown 格式。\n\n# Constraints & Rules\n1. **纯净输出**：直接输出识别后的内容，**严禁**包含任何开场白（如“好的”、“这是识别结果”）、结束语或自我解释。\n2. **噪音清洗**：\n   - 自动检测并删除页眉、页脚、页码。\n   - 删除扫描产生的噪点字符或无意义的各种符号。\n   - 忽略手写笔记或涂鸦（除非显式要求保留）。\n3. **断行修复**：\n   - 英文单词若因换行被连字符“-”切断，请自动合并为一个完整单词。\n   - 中文段落若因换行被打断，请自动合并为同一段落，不要保留硬回车。\n4. **格式保留**：\n   - **标题**：根据字体大小和层级，使用 Markdown 的 #, ##, ### 标记。\n   - **列表**：识别项目符号，使用 - 或 1. 格式化。\n   - **代码**：如果遇到代码块，使用 ```language ... ``` 包裹。\n   - **公式**：如果遇到数学公式，请使用 LaTeX 格式（行内使用 $...$，块级使用 $$...$$）。\n   - **表格**：将表格转换为标准的 Markdown 表格。\n5. **纠错机制**：基于上下文修正明显的 OCR 识别错误（例如将“l”误识别为“1”，将“微”误识别为“徵”），但严禁篡改原文语义。\n\n# Workflow\n1. 分析图像布局，区分正文、标题、边栏和噪音。\n2. 执行文字识别。\n3. 应用上述清洗和格式化规则。\n4. 输出最终 Markdown 文本。")
    
    # Output subdirectory
    model_subdir_name = model_id.replace("/", "_").replace(":", "_")
    output_dir = base_res_dir / model_subdir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Model ID: {model_id}")
    logger.info(f"Settings: max_tokens={max_tokens}, output_dir={output_dir}")
    logger.info(f"Input Prompt:\n{prompt_text}")
    
    extensions = {'.png', '.jpg', '.jpeg'}
    if not pic_dir.exists():
        logger.error(f"Input directory not found: {directory_path}")
        return

    # Filter for test_file if specified
    if test_file:
        files = [pic_dir / test_file] if (pic_dir / test_file).exists() else []
    else:
        files = sorted([f for f in pic_dir.iterdir() if f.suffix.lower() in extensions])
        
    if not files:
        logger.warning(f"No files to process {'(Test file ' + test_file + ' not found)' if test_file else ''}")
        return

    for file_path in files:
        logger.info(f"Processing File: {file_path.name}")
        base64_image = encode_image(file_path)
        logger.info(f"Input Image Size: {len(base64_image)} bytes")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                start_time = datetime.now()
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                            ],
                        }
                    ],
                    max_tokens=max_tokens,
                )
                duration = (datetime.now() - start_time).total_seconds()
                
                content = response.choices[0].message.content
                usage = response.usage
                
                if content:
                    output_file = output_dir / f"{file_path.stem}.md"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    logger.info(f"SUCCESS: {file_path.name} -> {output_file.name}")
                    logger.info(f"Metrics: Time={duration:.2f}s | Tokens: Total={usage.total_tokens} (P={usage.prompt_tokens}, C={usage.completion_tokens})")
                    logger.info(f"Preview: {content[:100].replace('\n', ' ')}...")
                else:
                    logger.warning(f"No content extracted for {file_path.name}")
                
                break # Success, break the retry loop
            
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 3
                    logger.warning(f"Error processing {file_path.name} (Attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to process {file_path.name} after {max_retries} attempts: {str(e)}")
        
        logger.info("-" * 40)
        
        # If testing, stop after one file as requested
        if test_file:
            logger.info("Test file processed. Stopping as requested.")
            break

    logger.info("Task Finished.")

if __name__ == "__main__":
    base_path = Path(__file__).parent / "testdata"
    # To run test on specific file:
    # process_images(base_path / "pic", base_path / "results", test_file="3_00.jpg")
    # To run full batch:
    process_images(base_path / "pic", base_path / "results")