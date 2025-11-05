
# 修复"文本不匹配"错误

## 🎯 你遇到的问题

```
[1/12] 处理 11d76b912e-c3c9-456c-a895-7f4778e6a43f... ✗ (文本不匹配 - 预期: '恭喜您達成非凡里程碑!...', 实际: '...')
```

**所有 12 个翻译都失败了**，错误显示：
- 预期：有具体的文本内容
- 实际：`'...'`（空的）

---

## 🔍 问题原因分析

### 可能的原因

1. **Word 文档的 Target 列实际为空**
   - 这是一个新文档，还没有翻译
   - 或者是模板文档

2. **python-docx 无法正确读取单元格内容**
   - 单元格使用了特殊格式
   - 内容在文本框或域代码中
   - 单元格有复杂的 XML 结构

3. **对照表中的 old_text 与实际内容不匹配**
   - 空格、标点符号差异
   - MarkItDown 提取的内容与实际 Word 不一致

---

## 🛠️ 诊断步骤

### 步骤 1：诊断 Word 文档（最重要）

运行诊断脚本检查 Word 文档的实际内容：

```bash
python3 diagnose_word_document.py \
  "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  "/Users/hua/md腳本/translations.json"
```

这会告诉你：
- ✓ Word 文档中是否有表格
- ✓ Target 列是否真的有内容
- ✓ 为什么 python-docx 读取为空
- ✓ 具体的修复建议

### 步骤 2：手动检查 Word 文档

在 Word 中打开文档：
```bash
open "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx"
```

检查：
1. **Target 列是否有内容？**
   - 如果为空 → 这是正常的，需要修改对照表的 old_text 为空
   - 如果有内容 → python-docx 读取有问题

2. **内容格式是否特殊？**
   - 是否使用了文本框？
   - 是否有域代码（按 Alt+F9 查看）？
   - 是否有复杂的格式？

### 步骤 3：查看对照表

```bash
head -50 /Users/hua/md腳本/translations.json
```

检查 old_text 的内容是否合理。

---

## ✅ 解决方案

### 方案 A：如果 Target 列确实为空（最可能）

修改对照表，将所有 old_text 设置为空字符串：

```python
# 创建一个脚本来修改对照表
cat > fix_translations.py << 'EOF'
import json

with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 将所有 old_text 设为空
for trans in data['translations']:
    trans['old_text'] = ''

# 保存
with open('translations_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✓ 已生成 translations_fixed.json")
print("  所有 old_text 已设为空")
EOF

python3 fix_translations.py
```

然后重新运行：
```bash
python3 update_fc_insider_simple.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --translations translations_fixed.json \
  --output "/Users/hua/md腳本/output.docx" \
  --author "Gemini"
```

### 方案 B：使用模糊匹配

如果 Target 列有内容，但匹配失败（空格、标点差异），使用模糊匹配脚本：

```bash
python3 update_fc_insider_fuzzy.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --translations "/Users/hua/md腳本/translations.json" \
  --output "/Users/hua/md腳本/output.docx" \
  --author "Gemini" \
  --fuzzy
```

**优势**：
- 忽略空格、标点差异
- 支持包含匹配
- 更高的成功率

### 方案 C：使用详细模式诊断

如果仍然失败，使用详细模式查看具体的匹配情况：

```bash
python3 update_fc_insider_fuzzy.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --translations "/Users/hua/md腳本/translations.json" \
  --output "/Users/hua/md腳本/output.docx" \
  --author "Gemini" \
  --fuzzy \
  --verbose
```

这会显示每一行的：
- 预期的 old_text
- 实际的文本
- 匹配结果

---

## 📋 完整的诊断和修复流程

### 流程图

```
1. 运行诊断脚本
   ↓
2. 确认问题原因
   ↓
3a. Target 列为空？        3b. Target 列有内容？
    ↓                          ↓
    修改对照表                使用模糊匹配
    (old_text = '')            (--fuzzy)
    ↓                          ↓
4. 重新运行更新脚本
   ↓
5. 检查输出文档
```

### 详细命令

```bash
# 1. 诊断
python3 diagnose_word_document.py \
  "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  "/Users/hua/md腳本/translations.json"

# 2. 根据诊断结果选择方案

# 方案 A：Target 列为空
# 使用上面的 fix_translations.py 脚本

# 方案 B：使用模糊匹配
python3 update_fc_insider_fuzzy.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --translations "/Users/hua/md腳本/translations.json" \
  --output "/Users/hua/md腳本/output.docx" \
  --author "Gemini" \
  --fuzzy \
  --verbose

# 3. 检查输出
open "/Users/hua/md腳本/output.docx"
```

---

## 🤔 常见问题

### Q1: 为什么会显示 `实际: '...'`？

**A:** 这说明 python-docx 读取单元格时得到的是空字符串。可能原因：
1. 单元格确实为空
2. 内容在特殊位置（文本框、域代码）
3. python-docx 无法识别该格式

### Q2: MarkItDown 明明提取到了内容，为什么 python-docx 读不到？

**A:** MarkItDown 和 python-docx 使用不同的方法：
- **MarkItDown**：转换整个文档为 Markdown（更全面）
- **python-docx**：直接读取单元格的文本属性（可能遗漏特殊格式）

**解决**：
1. 如果 MarkItDown 能读到，说明内容确实存在
2. 可能需要在 Word 中清理格式（复制 → 粘贴为纯文本）
3. 或者使用 MarkItDown 提取的内容作为参考，手动创建对照表

### Q3: 能不能直接基于 MarkItDown 的结果更新文档？

**A:** 可以，但需要额外的步骤：

```bash
# 1. 用 MarkItDown 提取当前内容
python3 extract_table_markitdown.py input.docx current_table.md

# 2. 从 Markdown 解析当前的 Target 内容
python3 generate_translation_mapping.py \
  --markdown current_table.md \
  --new-translations new_translations.json \
  --output translations.json

# 3. 这样对照表的 old_text 就是从 Markdown 提取的内容

# 4. 但是更新时仍然需要与 Word 文档匹配
# 如果不匹配，使用 --fuzzy
```

---

## 💡 最佳实践

### 1. 始终先诊断

```bash
python3 diagnose_word_document.py input.docx translations.json
```

### 2. 使用模糊匹配

```bash
python3 update_fc_insider_fuzzy.py ... --fuzzy
```

### 3. 详细模式调试

```bash
python3 update_fc_insider_fuzzy.py ... --fuzzy --verbose
```

### 4. 保持文档格式简单

- 避免使用文本框
- 避免使用域代码
- 使用纯文本格式

---

## 🚀 立即行动

### 第一步：诊断

```bash
python3 diagnose_word_document.py \
  "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  "/Users/hua/md腳本/translations.json"
```

### 第二步：根据诊断结果

**如果显示"所有 Target 列都为空"**：
```bash
# 修改对照表
python3 fix_translations.py

# 重新运行
python3 update_fc_insider_simple.py \
  --input "..." \
  --translations translations_fixed.json \
  --output "..."
```

**如果显示"Target 列有内容"**：
```bash
# 使用模糊匹配
python3 update_fc_insider_fuzzy.py \
  --input "..." \
  --translations "..." \
  --output "..." \
  --fuzzy \
  --verbose
```

### 第三步：查看输出并分享结果

请运行诊断命令并分享输出，我会根据具体情况提供精确的解决方案！

---

## 📚 相关工具

| 工具 | 用途 |
|------|------|
| `diagnose_word_document.py` | 诊断 Word 文档结构 |
| `update_fc_insider_fuzzy.py` | 模糊匹配更新（推荐） |
| `update_fc_insider_simple.py` | 精确匹配更新 |
| `debug_markdown_parsing.py` | 诊断 Markdown 解析 |

---

## 🎯 总结

### 问题

所有翻译都显示"文本不匹配 - 实际: '...'"

### 原因

1. **最可能**：Word 文档的 Target 列为空
2. 其他：python-docx 无法读取特殊格式

### 解决

1. **诊断**：运行 `diagnose_word_document.py`
2. **修复**：
   - Target 列为空 → 修改对照表（old_text = ''）
   - Target 列有内容 → 使用模糊匹配（--fuzzy）

**立即运行诊断命令获取答案！** 🔍
