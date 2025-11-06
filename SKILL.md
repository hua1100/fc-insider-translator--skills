---
name: fc-document-tracking-changes
description: 处理 Word 文档翻译更新，使用追踪修订标记变更。支持智能匹配新旧翻译（顺序无关）、自动过滤占位符行、处理已有追踪修订的文档。当用户需要更新 Word 文档翻译、处理 DOCX 表格翻译、提到"tracked changes"、"追踪修订"、"translation mapping"、"翻译对照"时使用。
version: 2.0
---

# FC Document Tracking Changes Skill

## 🎯 核心功能

- **智能匹配** - 使用文本相似度自动配对，顺序无关
- **追踪修订** - 自动检测和处理已有追踪修订的文档
- **占位符过滤** - 自动跳过 `"<0/>"在第 <1/> 頁` 等占位符行
- **一键执行** - 完整自动化工作流程，从 Word 到 Word

---

## 📦 安装依赖

首次使用前，安装必需的依赖：

```bash
pip install python-docx lxml markitdown[docx]
```

⚠️ **重要**：必须安装 `markitdown[docx]`（包含 [docx]），而不是 `markitdown`

完整依赖说明见 [PARAMETERS.md](references/PARAMETERS.md#依赖要求)

---

## 🚀 快速开始

### 方式 1: 一键执行（推荐）

```bash
python3 scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx"
```

**提示**：默认作者为 "Claire"，可以省略 `--author` 参数。如需修改作者，添加 `--author "Your Name"`

**就这么简单！** 脚本会自动完成表格提取、智能匹配、应用追踪修订。

### 方式 2: 分步执行

```bash
# 步骤 1: 提取表格
python3 scripts/extract_table_markitdown_simple.py \
  --input "input.docx" \
  --output "extracted_table.md"

# 步骤 2: 生成翻译映射（智能匹配）
python3 scripts/generate_translation_mapping.py \
  --markdown "extracted_table.md" \
  --new-translations "new_translations.txt" \
  --output "translations.json" \
  --match-by smart \
  --verbose

# 步骤 3: 应用翻译（默认作者：Claire）
python3 scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --mode auto \
  --verbose
```

---

## 📋 工作流程

```
输入
├─ input.docx (Word 文档，四列表格)
└─ new_translations.txt (新翻译，每行一个，顺序可不一致)
    ↓
[步骤 1] extract_table_markitdown_simple.py
    使用 MarkItDown 提取表格为 Markdown
    ↓
extracted_table.md
    ↓
[步骤 2] generate_translation_mapping.py
    • 自动过滤占位符行
    • 智能匹配新旧翻译
    • 计算文本相似度
    ↓
translations.json (翻译映射表)
    ↓
[步骤 3] update_fc_insider_tracked.py
    • 自动检测文档类型
    • 处理已有追踪修订
    • 应用新的追踪修订
    ↓
output.docx (含追踪修订的输出文档)
```

---

## 🛠️ 核心脚本

### extract_table_markitdown_simple.py
从 Word 文档提取表格，转换为 AI 友好的 Markdown 格式。使用 Microsoft MarkItDown，专为 LLM 优化。

### generate_translation_mapping.py
生成新旧翻译映射表。支持智能匹配（顺序无关）、segment_id 匹配、index 匹配三种模式。自动过滤占位符行。

### update_fc_insider_tracked.py
将翻译应用到 Word 文档，使用追踪修订标记变更。自动检测文档类型，支持三种读取模式（auto/read_deleted/read_inserted）。

### run_complete_workflow.py
一键执行完整工作流程。自动调用上述三个脚本，管理临时文件，提供依赖检查。

### analyze_word_structure_deep.py
深度诊断工具。分析 Word 文档结构，识别问题，提供解决方案建议。仅在遇到问题时使用。

---

## 📝 输入文件格式

### 新翻译文件（纯文本，推荐）

```txt
PY26 正式啟動！作為創辦人理事會領袖...
您是團隊的榜樣。為協助您更輕鬆且...
請聆聽安麗市場事業總裁 John Parker...
```

**要求**：
- 每行一个翻译
- 不包含占位符行
- 顺序可以不一致（使用 `--match-by smart`）
- 行数需要与过滤后的表格行数一致

---

## 📚 完整文档

### 详细指南
- **[PARAMETERS.md](references/PARAMETERS.md)** - 完整参数说明
- **[TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)** - 故障排查指南
- **[BEST_PRACTICES.md](references/BEST_PRACTICES.md)** - 使用最佳实践
- **[ADVANCED.md](references/ADVANCED.md)** - 高级功能详解

### 核心技术
- **[SMART_MATCHING_GUIDE.md](references/SMART_MATCHING_GUIDE.md)** - 智能匹配详解
- **[TRACKED_CHANGES_SOLUTION.md](references/TRACKED_CHANGES_SOLUTION.md)** - 追踪修订处理
- **[PLACEHOLDER_FILTER_GUIDE.md](references/PLACEHOLDER_FILTER_GUIDE.md)** - 占位符过滤
- **[MAPPING_MECHANISM_EXPLAINED.md](references/MAPPING_MECHANISM_EXPLAINED.md)** - 映射机制详解

---

## 💡 快速提示

### 遇到映射不正确？
使用 `--match-by smart --verbose` 查看匹配详情和相似度分数。

### 遇到更新失败？
运行诊断工具：
```bash
python3 scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "segment-id" \
  --verbose
```

### 行数不匹配？
检查新翻译文件是否包含占位符行。使用 `--verbose` 查看哪些行被过滤。

---

## 📊 版本信息

**当前版本**：v2.0

**主要特性**：
- 智能匹配功能
- 追踪修订自动处理
- 占位符自动过滤
- 一键执行脚本
- 深度诊断工具
