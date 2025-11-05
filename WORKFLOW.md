# FC Insider 翻译工作流程（混合方案）

## 概述

这个改进的工作流程将 **读取（Word → Markdown）** 和 **写入（XML + 追踪修订）** 分离，解决了 AI 在直接解析 Word XML 时常见的问题。

### 为什么需要混合方案？

**原始问题**：
- AI 直接读取 Word XML 结构容易出错
- 判断表格为空、单元格定位失败等问题
- XML 结构复杂，调试困难

**解决方案**：
- **读取阶段**：Word → Markdown（AI 友好格式）
- **分析阶段**：AI 基于 Markdown 生成对照表
- **写入阶段**：保持原有的 XML + 追踪修订方法（已验证有效）

---

## 完整工作流程

### 阶段 1：Word → Markdown（提取表格）

使用 `extract_table_to_markdown.py` 将 Word 表格转换为 Markdown：

```bash
# 方法 1：使用 Pandoc（推荐，快速）
python extract_table_to_markdown.py input.docx table.md

# 方法 2：使用 docx2python（精细控制）
python extract_table_to_markdown.py input.docx table.md --method docx2python

# 同时生成 JSON 结构化数据
python extract_table_to_markdown.py input.docx table.md --output-json table.json
```

**输出示例（table.md）**：
```markdown
# FC Insider Translation Table

## Table 1

| Segment ID | Status | Source | Target |
|------------|--------|--------|--------|
| 7bb0408a-1 | Final | Hello world | 你好世界 |
| 7bb0408a-2 | Final | How are you? | 你好吗？ |
| ... | ... | ... | ... |
```

**优点**：
- ✅ AI 可以轻松读取和理解表格
- ✅ 不会出现"表格为空"等误判
- ✅ 可以轻松验证提取是否正确

---

### 阶段 2：AI 生成新译文

**选项 A：手动提供新译文 JSON**

```json
{
  "7bb0408a-1": "更好的翻译 1",
  "7bb0408a-2": "更好的翻译 2"
}
```

**选项 B：让 AI 基于 Markdown 生成译文**

提示词示例：
```
基于以下 Markdown 表格，请改进所有译文并输出为 JSON 格式：
{"segment_id": "new_translation", ...}

[粘贴 table.md 内容]
```

**选项 C：使用外部翻译工具**

将 Source 列提取出来，发送给翻译 API，然后整理为 JSON。

---

### 阶段 3：生成新旧翻译对照表

使用 `generate_translation_mapping.py` 生成 `translations.json`：

```bash
# 从 Markdown 表格 + 新译文 JSON 生成对照表
python generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_translations.json \
  --output translations.json
```

**输出（translations.json）**：
```json
{
  "translations": [
    {
      "segment_id": "7bb0408a-1",
      "old_text": "你好世界",
      "new_text": "更好的翻译 1"
    },
    {
      "segment_id": "7bb0408a-2",
      "old_text": "你好吗？",
      "new_text": "更好的翻译 2"
    }
  ]
}
```

**验证和预览**：

```bash
# 预览变更（不保存文件）
python generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_translations.json \
  --preview-only
```

---

### 阶段 4：解包 Word 文档

```bash
python /mnt/skills/public/docx/ooxml/scripts/unpack.py input.docx unpacked/
```

**记录 RSID**（从输出中复制）：
```
Suggested RSID for new content: 00AB12CD
```

---

### 阶段 5：应用追踪修订（写入）

使用原有的 `update_fc_insider_v3.py`：

```bash
python update_fc_insider_v3.py \
  --unpacked unpacked/ \
  --translations translations.json \
  --rsid 00AB12CD \
  --author "Your Name"
```

**这一步仍使用 XML 方法**，因为：
- ✅ 追踪修订需要精确的 XML 控制
- ✅ 已有成熟的实现
- ✅ 不需要重构

---

### 阶段 6：打包 Word 文档

```bash
python /mnt/skills/public/docx/ooxml/scripts/pack.py \
  unpacked/ \
  output_with_tracking.docx
```

---

## 自动化脚本

创建一个端到端的自动化脚本 `run_translation_workflow.sh`：

```bash
#!/bin/bash
# FC Insider 翻译工作流程自动化

set -e  # 遇到错误立即退出

INPUT_DOCX="$1"
NEW_TRANSLATIONS="$2"
OUTPUT_DOCX="${3:-output_with_tracking.docx}"
AUTHOR="${4:-Claude}"

if [ -z "$INPUT_DOCX" ] || [ -z "$NEW_TRANSLATIONS" ]; then
    echo "用法: $0 <input.docx> <new_translations.json> [output.docx] [author]"
    exit 1
fi

echo "=========================================="
echo "FC Insider 翻译工作流程"
echo "=========================================="

# 阶段 1：提取表格
echo "[1/6] 提取表格为 Markdown..."
python extract_table_to_markdown.py "$INPUT_DOCX" table.md

# 阶段 2：生成对照表
echo "[2/6] 生成翻译对照表..."
python generate_translation_mapping.py \
  --markdown table.md \
  --new-translations "$NEW_TRANSLATIONS" \
  --output translations.json

# 阶段 3：解包 Word
echo "[3/6] 解包 Word 文档..."
python /mnt/skills/public/docx/ooxml/scripts/unpack.py "$INPUT_DOCX" unpacked/ > unpack.log
RSID=$(grep "Suggested RSID" unpack.log | awk '{print $NF}')
echo "RSID: $RSID"

# 阶段 4：应用追踪修订
echo "[4/6] 应用追踪修订..."
python update_fc_insider_v3.py \
  --unpacked unpacked/ \
  --translations translations.json \
  --rsid "$RSID" \
  --author "$AUTHOR"

# 阶段 5：打包 Word
echo "[5/6] 打包 Word 文档..."
python /mnt/skills/public/docx/ooxml/scripts/pack.py \
  unpacked/ \
  "$OUTPUT_DOCX"

# 清理临时文件
echo "[6/6] 清理临时文件..."
rm -rf unpacked/ table.md unpack.log

echo "=========================================="
echo "✓ 完成！输出文件: $OUTPUT_DOCX"
echo "=========================================="
```

---

## 工作流程对比

### 原始方案（直接 XML）
```
Word DOCX
  ↓
解包 → XML
  ↓
AI 直接解析 XML（容易出错 ❌）
  ↓
修改 XML + 追踪修订
  ↓
打包 → Word DOCX
```

### 混合方案（推荐）
```
Word DOCX
  ↓
├─→ [读取] → Markdown → AI 分析（准确 ✅）
│                ↓
│              对照表 (translations.json)
│                ↓
└─→ [写入] ← 解包 → XML 修改 + 追踪修订（已验证 ✅）
  ↓
打包 → Word DOCX
```

---

## 优势总结

### 读取阶段（Word → Markdown）
- ✅ AI 友好：Markdown 简单清晰
- ✅ 不会误判表格为空
- ✅ 易于验证提取结果
- ✅ 支持多种转换工具（Pandoc、docx2python）

### 分析阶段（生成对照表）
- ✅ 结构化数据，易于调试
- ✅ 可预览变更
- ✅ 支持人工验证和修改

### 写入阶段（XML + 追踪修订）
- ✅ 保持原有成熟实现
- ✅ 精确的追踪修订控制
- ✅ 保留格式和样式

---

## 依赖安装

### Pandoc（推荐）
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# Windows
# 从 https://pandoc.org/installing.html 下载安装
```

### docx2python（可选）
```bash
pip install docx2python
```

---

## 故障排查

### 问题 1：Pandoc 未安装
```
✗ 错误：未找到 Pandoc
```

**解决**：按照上述"依赖安装"部分安装 Pandoc

### 问题 2：表格提取结果不正确
```
# 尝试使用 docx2python 方法
python extract_table_to_markdown.py input.docx table.md --method docx2python
```

### 问题 3：segment_id 匹配失败
```
# 使用行索引匹配
python generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.txt \
  --match-by index
```

### 问题 4：追踪修订未生效

检查：
```bash
# 检查对照表
cat translations.json

# 检查 XML 中的追踪修订标记
grep -c '<w:del>' unpacked/word/document.xml
grep -c '<w:ins>' unpacked/word/document.xml
```

---

## 下一步改进

1. **GUI 工具**：创建图形界面简化流程
2. **批量处理**：支持多个文档同时处理
3. **翻译 API 集成**：直接调用 DeepL、Google Translate 等
4. **智能对照**：基于相似度匹配而非严格 segment_id

---

## 总结

混合方案通过分离读写关注点，显著提升了 AI 处理 FC Insider 翻译更新的准确性和可靠性：

- **读取**：简单、准确、易验证（Markdown）
- **写入**：精确、成熟、保留格式（XML）
- **中间层**：结构化对照表，易于调试和验证

这种架构既解决了 AI 解析 XML 的困难，又保持了追踪修订的精确控制。
