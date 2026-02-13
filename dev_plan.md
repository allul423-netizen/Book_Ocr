## 📅 PageIndex 结构化识别系统：分步开发计划

### 第一阶段：环境搭建与基础设施

**目标**：建立两个互不干扰的 Python 虚拟环境。

1. **环境 A：Vision (图像处理)**
   - **版本**：Python 3.10
   - **核心**：安装 `paddlepaddle` 和 `paddleocr==2.7.3` (CPU版或根据情况调整)。
   - **关键动作**：手动强制安装 `numpy==1.26.4`。
   - **验证**：确保 `import paddle` 和 `import cv2` 不报错。
2. **环境 B：LLM (大模型与拼接)**
   - **版本**：Python 3.12
   - **核心**：安装 `openai`, `pillow`, `python-dotenv`。
3. **目录规范建立**：
   - 创建 `input/`、`output/` 及子目录。
   - 将你提供的 3 个示范代码放入 `ref/` 文件夹。

------

### 第二阶段：视觉预处理模块开发

**目标**：基于环境 A，将原始图片转化为可供识别的“规范化碎片”。

1. **子任务 2.1：旋转校正 (`rotate_handler.py`)**
   - **参考**：`ref/open_cv_test.py`
   - **逻辑**：实现自动纠偏，并将校正后的图片存入 `output/[folder]/step1_rotated/`。
2. **子任务 2.2：版面分割 (`segment_handler.py`)**
   - **参考**：`ref/paddle_OCR_test.py`
   - **逻辑**：调用 PP-Structure。
   - **过滤逻辑**：仅保留 `title`, `text`, `figure`, `table` 类型的切片。
   - **保存规则**：按照 `crop_{index}_{type}.png` 命名，存入 `step2_crops/`。
3. **日志生成**：
   - 脚本运行结束时，在 `output/[folder]` 下创建 `processing_log.txt`，记录成功分割的切片数量。

------

### 第三阶段：智能识别与尺寸补齐

**目标**：基于环境 B，解决 API 分辨率限制并进行内容识别。

1. **子任务 3.1：补白预处理 (`padding_handler.py`)**
   - **核心逻辑**：检查每一个 crop 图片。
   - **56px 策略**：若长或宽小于 56px，使用 Pillow 在四周填充白色背景，确保不触发 SiliconFlow 的报错。
2. **子任务 3.2：LLM 识别 (`llm_handler.py`)**
   - **参考**：`ref/ocr_minimal_test.py`
   - **逻辑**：遍历补白后的切片，调用 SiliconFlow 的 `Qwen/Qwen3-VL-8B-Instruct`。
   - **Prompt 设置**：根据文件名中的 `type` 动态调整 Prompt（例如：针对 `table` 要求输出 Markdown Table）。
   - **输出**：在 `step3_md_fragments/` 下生成同名的 `.md` 文件。

------

### 第四阶段：灵活拼接与日志汇总

**目标**：实现用户可控的文档整合。

1. **子任务 4.1：按需拼接程序 (`merger.py`)**
   - **输入方式**：程序启动后，用户输入 `input` 目录下的文件夹名称。
   - **排序算法**：
     - 第一优先级：`title`（按序号）
     - 第二优先级：`text`（按序号）
     - 第三优先级：`figure` & `table`
   - **输出**：在对应的 `output` 目录下生成 `final_result.md`。
2. **子任务 4.2：全流程日志审计**
   - 最终汇总 `processing_log.txt`，列出哪些文件因为尺寸过小被补白，哪些文件处理成功，哪些识别失败。

------

### 第五阶段：集成总控

**目标**：解决跨环境调用的自动化。

1. **开发 `pipeline_run.py`**：
   - 编写一个顶层脚本，使用 `subprocess` 先调用 `env_vision` 的 Python 执行第一、二阶段。
   - 接着调用 `env_llm` 的 Python 执行第三、四阶段。
2. **全量测试**：
   - 将一批包含倾斜图片、极小表格、长文本的混合文档放入 `input/`。
   - 检查 `output/` 结果是否符合结构化预期。

------

### 💡 核心交付物 Checklist

- [ ] **环境隔离配置表**（记录两个环境的 pip list）。
- [ ] **四个功能脚本**：`vision_processor.py`, `llm_recognizer.py`, `doc_merger.py`, `pipeline_run.py`。
- [ ] **三份示范代码引用记录**：在代码注释中明确标注参考了 `ref/` 中的哪些逻辑。
- [ ] **自动化日志记录系统**（记录每个阶段的 Input/Output）。
