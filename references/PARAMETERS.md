# 参数说明

完整的参数参考文档，涵盖所有脚本的参数选项。

---

## 依赖要求

在使用脚本之前，请确保安装以下依赖。

### 必需依赖

| 包名 | 安装命令 | 用途 |
|------|----------|------|
| `python-docx` | `pip install python-docx` | 读写 Word 文档 |
| `lxml` | `pip install lxml` | XML 解析（追踪修订需要） |
| `markitdown[docx]` | `pip install markitdown[docx]` | 提取 Word 表格（⚠️ 注意必须包含 [docx]） |

### ⚠️ 重要提示

**必须安装 `markitdown[docx]`，而不是 `markitdown`**

```bash
# ✓ 正确
pip install markitdown[docx]

# ✗ 错误 - 无法读取 .docx 文件
pip install markitdown
```

`markitdown[docx]` 会额外安装：
- `mammoth` - 用于读取 Word 文档
- 其他 docx 处理依赖

### 验证安装

```bash
# 验证所有依赖
python3 -c "import docx, lxml, markitdown, mammoth; print('✓ 所有依赖已安装')"
```

或者使用自动检查：

```bash
# run_complete_workflow.py 会自动检查依赖
python3 ../scripts/run_complete_workflow.py --help
```

### 可选：一次性安装

```bash
# 安装所有依赖
pip install python-docx lxml markitdown[docx]

# 或使用 requirements.txt（如果提供）
pip install -r requirements.txt
```

---

## 通用参数

适用于所有脚本的通用参数。

| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `--input` | 输入 Word 文档路径 | ✅ | - |
| `--output` | 输出文档路径 | ✅ | - |
| `--verbose` | 显示详细信息（强烈推荐） | ❌ | False |

---

## run_complete_workflow.py

一键执行完整工作流程。

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--input` | 输入 Word 文档路径 | `"input.docx"` |
| `--new-translations` | 新翻译文件路径（纯文本或 JSON） | `"new_translations.txt"` |
| `--output` | 输出 Word 文档路径 | `"output.docx"` |

### 可选参数

| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| `--author` | 追踪修订作者名称 | 任意文本 | `"Translator"` |
| `--match-by` | 匹配方式 | `smart`, `segment_id`, `index` | `smart` |
| `--update-mode` | 更新模式 | `auto`, `read_deleted`, `read_inserted` | `auto` |
| `--keep-temp` | 保留临时文件（用于调试） | - | False |
| `--verbose` | 显示详细输出 | - | False |
| `--skip-dependencies-check` | 跳过依赖检查（不推荐） | - | False |

### 使用示例

```bash
# 基本用法（使用默认作者 Claire.lee@amway.com）
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx"

# 详细模式
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --verbose

# 自定义匹配方式和作者
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "translator@company.com" \
  --match-by index \
  --update-mode read_inserted
```

---

## extract_table_markitdown_simple.py

从 Word 文档提取表格，转换为 Markdown 格式。

### 参数

| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `--input` | 输入 Word 文档路径 | ✅ | - |
| `--output` | 输出 Markdown 文件路径 | ✅ | - |

### 使用示例

```bash
python3 ../scripts/extract_table_markitdown_simple.py \
  --input "input.docx" \
  --output "extracted_table.md"
```

---

## generate_translation_mapping.py

生成新旧翻译映射表。

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--markdown` | 提取的 Markdown 表格路径 | `"extracted_table.md"` |
| `--new-translations` | 新翻译文件路径 | `"new_translations.txt"` |
| `--output` | 输出 JSON 映射表路径 | `"translations.json"` |

### 可选参数

| 参数 | 说明 | 可选值 | 默认值 | 推荐 |
|------|------|--------|--------|------|
| `--match-by` | 匹配方式 | `smart`, `segment_id`, `index` | `segment_id` | `smart` ⭐ |
| `--skip-placeholder-filter` | 跳过占位符过滤 | - | False | 不建议 |
| `--verbose` | 显示详细信息 | - | False | 建议 ✅ |

### 匹配方式详解

#### smart（推荐 ⭐⭐⭐⭐⭐）

使用文本相似度自动配对，顺序无关。

**特点**：
- ✅ 顺序无关
- ✅ 自动配对
- ✅ 容错能力强
- ✅ 显示相似度分数

**适用场景**：
- 新翻译顺序与原表格不一致
- 不确定顺序是否正确
- 想要看到匹配的可信度

**示例**：
```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json" \
  --match-by smart \
  --verbose
```

#### segment_id（安全 ⭐⭐⭐⭐）

通过 segment_id 精确匹配，顺序无关。

**特点**：
- ✅ 顺序无关
- ✅ 精确匹配
- ❌ 需要 JSON 格式
- ❌ 需要准备 segment_id

**适用场景**：
- 有准确的 segment_id 映射
- 新翻译来自数据库或 API

**示例**：
```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.json" \
  --output "translations.json" \
  --match-by segment_id
```

**JSON 格式**：
```json
{
  "1360baf04e-73fb-432d-abf1-a0887de5f16a": "新翻译1",
  "1460baf04e-73fb-432d-abf1-a0887de5f16a": "新翻译2"
}
```

#### index（简单但脆弱 ⭐⭐⭐）

按行索引匹配，顺序必须完全一致。

**特点**：
- ✅ 简单直接
- ✅ 纯文本即可
- ❌ 顺序必须一致
- ❌ 容易出错

**适用场景**：
- 100% 确定顺序一致
- 一次性全量更新

**示例**：
```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json" \
  --match-by index
```

---

## update_fc_insider_tracked.py

将翻译应用到 Word 文档，使用追踪修订标记变更。

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--input` | 输入 Word 文档路径 | `"input.docx"` |
| `--translations` | 翻译映射表路径 | `"translations.json"` |
| `--output` | 输出 Word 文档路径 | `"output.docx"` |

### 可选参数

| 参数 | 说明 | 可选值 | 默认值 | 推荐 |
|------|------|--------|--------|------|
| `--mode` | 读取模式 | `auto`, `read_deleted`, `read_inserted` | `auto` | `auto` ⭐ |
| `--author` | 追踪修订作者 | 任意文本 | `"Translator"` | 你的名字 |
| `--verbose` | 显示详细信息 | - | False | 建议 ✅ |

### 读取模式详解

#### auto（推荐 ⭐⭐⭐⭐⭐）

自动检测文档类型。

**工作原理**：
1. 检查单元格是否包含追踪修订
2. 如果有 `<w:del>`，从删除的文本读取
3. 如果有 `<w:ins>`，从插入的文本读取
4. 如果都没有，从普通文本读取

**适用场景**：大多数情况

#### read_deleted

强制从删除的文本（`<w:delText>`）读取。

**适用场景**：
- 文档已有追踪修订
- 旧翻译在删除的文本中

#### read_inserted

强制从插入的文本（`<w:ins>` 中的 `<w:t>`）读取。

**适用场景**：
- 文档已有追踪修订
- 旧翻译在插入的文本中

### 使用示例

```bash
# 自动模式（推荐，使用默认作者）
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --mode auto \
  --verbose

# 指定模式和自定义作者
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "translator@company.com" \
  --mode read_inserted
```

---

## analyze_word_structure_deep.py

深度分析 Word 文档结构，诊断问题。

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--input` | 输入 Word 文档路径 | `"input.docx"` |

### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--sample-segment` | 要分析的 segment ID | 第一行 |
| `--export-xml` | 导出 XML 到文件 | False |
| `--export-json` | 导出 JSON 分析结果 | 不导出 |
| `--verbose` | 显示详细信息 | False |

### 使用示例

```bash
# 分析指定行
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "1360baf04e-73fb-432d-abf1-a0887de5f16a" \
  --verbose

# 导出 XML 和 JSON
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "1360baf04e-73fb-432d-abf1-a0887de5f16a" \
  --export-xml \
  --export-json "analysis.json"
```

---

## 参数组合建议

### 首次使用

```bash
# 使用详细模式，查看完整过程
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

### 生产环境

```bash
# 使用默认设置即可
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name"
```

### 调试问题

```bash
# 保留临时文件，详细输出
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --keep-temp \
  --verbose
```

### 顺序不一致

```bash
# 使用智能匹配
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --match-by smart \
  --verbose
```

---

## 常见问题

### Q: 我应该使用哪种匹配方式？

**A**: 推荐使用 `smart` 匹配方式：
- 顺序无关
- 自动配对
- 显示相似度
- 容错能力强

### Q: auto 模式和其他模式有什么区别？

**A**:
- `auto` - 自动检测文档类型，适合大多数情况
- `read_deleted` - 强制从删除的文本读取
- `read_inserted` - 强制从插入的文本读取

如果 `auto` 模式失败，使用诊断工具确定应该用哪种模式。

### Q: 什么时候需要使用 --verbose？

**A**: 建议总是使用 `--verbose`：
- 查看详细过程
- 了解匹配结果
- 发现潜在问题
- 调试错误

### Q: 为什么推荐使用 smart 而不是 segment_id？

**A**:
- `smart` 不需要准备 JSON，更简单
- `smart` 自动配对，不用担心顺序
- `smart` 显示相似度，更有信心

但如果你有准确的 segment_id 映射，`segment_id` 也是很好的选择。
