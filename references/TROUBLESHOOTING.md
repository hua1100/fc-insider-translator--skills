# 故障排查指南

遇到问题？这里提供完整的故障排查方案。

---

## 问题 1: 映射不正确

### 症状

生成的映射表中，新旧翻译配对错误。

```json
{
  "segment_id": "123abc...",
  "old_text": "应该配对的翻译A",
  "new_text": "但实际配对了翻译B"  // 错误！
}
```

### 原因

1. 使用了 `index` 匹配，但新翻译顺序与表格不一致
2. 新翻译包含了占位符行
3. 新翻译行数与过滤后的表格行数不匹配

### 解决方案

#### 方案 1: 使用智能匹配（推荐）

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown "extracted_table.md" \
  --new-translations "new_translations.txt" \
  --output "translations.json" \
  --match-by smart \
  --verbose
```

检查输出中的相似度分数：
```
匹配示例（按相似度排序）:
  1. 相似度: 87.34%  ← 高相似度，配对正确
     旧: PY26 已至，作為全球政策諮詢委員...
     新: PY26 正式啟動！作為創辦人理事會...
```

#### 方案 2: 检查占位符

使用 `--verbose` 查看哪些行被过滤：
```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown "extracted_table.md" \
  --new-translations "new_translations.txt" \
  --output "translations.json" \
  --verbose
```

输出会显示：
```
占位符过滤:
  总行数: 26
  保留: 13
  跳过: 13

跳过的占位符行（前10个）:
    1. 10ad6613a-...: "<0/>"在第 <1/> 頁
    2. 24efa4ea5-...: "<2/>"
```

确保你的新翻译文件有 **13 行**（不是 26 行）。

#### 方案 3: 检查行数

如果行数不匹配：
```
⚠️ 警告：
新翻译行数: 15
过滤后表格行数: 13
```

解决方法：
1. 删除新翻译文件中的占位符行
2. 确保行数与过滤后的表格一致

---

## 问题 2: 更新失败 - 文本不匹配

### 症状

```
[1/12] 处理 segment-id-123...
    ✗ 文本不匹配
    预期: 'PY26 已至，作為全球政策諮詢委員...'
    实际: '...' (空)
```

### 原因

1. 文档已有追踪修订，python-docx 无法读取
2. 单元格包含特殊格式或结构
3. 使用了错误的读取模式

### 解决方案

#### 步骤 1: 运行诊断工具

```bash
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "segment-id-123" \
  --verbose
```

#### 步骤 2: 查看诊断结果

**情况 A: 文档有追踪修订**

```
单元格结构分析:
  Run 数量: 0
  总字符数: 0
  追踪修订: 检测到 <w:del> 或 <w:ins> 元素

推荐解决方案:
  → 使用 update_fc_insider_tracked.py
  → 模式: read_deleted 或 read_inserted
```

**解决**：
```bash
# 使用自动模式（推荐）
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "Your Name" \
  --mode auto \
  --verbose
```

**情况 B: 普通文档**

```
单元格结构分析:
  Run 数量: 3
  总字符数: 45
  追踪修订: 无

推荐解决方案:
  → 使用 update_fc_insider_simple.py
```

#### 步骤 3: 使用推荐的脚本和模式

根据诊断结果选择合适的脚本。

---

## 问题 3: 行数不匹配

### 症状

```
⚠️ 警告：
新翻译行数: 15
过滤后表格行数: 13
✗ 新翻译行数不足！请检查新翻译文件
```

### 原因

新翻译文件行数与过滤后的表格行数不一致。

### 解决方案

#### 步骤 1: 查看过滤后的行数

运行脚本时会显示：
```
✓ 过滤后保留 13 行（跳过了占位符行）
```

#### 步骤 2: 检查新翻译文件

```bash
wc -l new_translations.txt
# 应该显示: 13 new_translations.txt
```

如果行数不对，检查是否包含了占位符行：
- `"<0/>"在第 <1/> 頁`
- `"<2/>"`
- `第 <12/> 頁`

#### 步骤 3: 调整新翻译文件

删除占位符行，确保只包含实际的翻译内容。

---

## 问题 4: 相似度过低警告

### 症状

```
⚠️ 警告：2 个配对的相似度较低（< 15%）
   建议检查这些配对是否正确：

   1. 相似度: 12.34%
      旧: 2025 年 9 月 // 第 8 期
      新: 2025/9/8 新財年，新希望！
```

### 原因

智能匹配发现某些配对的相似度很低，可能配对不正确。

### 解决方案

#### 方案 1: 检查低相似度配对

查看警告中列出的配对，确认是否正确。

如果配对正确（例如，翻译风格差异很大），可以继续使用。

如果配对错误，需要手动调整。

#### 方案 2: 调整最小相似度阈值

如果你觉得阈值太严格，可以修改脚本中的参数：

```python
# 在 generate_translation_mapping.py 中
new_translations = smart_match_translations(
    old_table,
    text_list,
    min_similarity=0.10,  # 降低阈值到 10%（默认 15%）
    verbose=args.verbose
)
```

#### 方案 3: 使用 segment_id 匹配

如果智能匹配不够准确，准备 JSON 格式的新翻译：

```json
{
  "segment-id-1": "准确的翻译1",
  "segment-id-2": "准确的翻译2"
}
```

然后使用 segment_id 匹配：
```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown "extracted_table.md" \
  --new-translations "new_translations.json" \
  --output "translations.json" \
  --match-by segment_id
```

---

## 问题 5: 依赖缺失

### 症状

```
✗ markitdown 未安装
✗ python-docx 未安装
```

### 解决方案

#### 自动安装（推荐）

脚本会提示是否安装：
```
⚠️ 缺少依赖，需要安装：
  pip install markitdown
  pip install python-docx

是否现在安装？(y/n): y
```

输入 `y` 自动安装。

#### 手动安装

```bash
pip install markitdown python-docx lxml
```

#### 跳过依赖检查（不推荐）

```bash
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --skip-dependencies-check
```

---

## 问题 6: auto 模式检测错误

### 症状

```
[1/12] 处理 segment-id-123...
    自动检测到文本来源: deleted
    ✗ 文本不匹配
    预期: '旧翻译'
    实际: '其他内容'
```

### 原因

auto 模式检测到了追踪修订，但读取了错误的文本来源。

### 解决方案

#### 步骤 1: 使用诊断工具

```bash
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "segment-id-123" \
  --export-xml \
  --verbose
```

#### 步骤 2: 检查 XML 输出

查看 `target_cell.xml`，确认旧翻译在哪里：
- 在 `<w:delText>` 中 → 使用 `read_deleted`
- 在 `<w:ins>` 的 `<w:t>` 中 → 使用 `read_inserted`

#### 步骤 3: 使用正确的模式

```bash
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "Your Name" \
  --mode read_inserted \  # 或 read_deleted
  --verbose
```

---

## 问题 7: 输出文档无法打开

### 症状

Word 提示"文件已损坏"或无法打开。

### 原因

1. 输入文档格式有问题
2. 更新过程中出错

### 解决方案

#### 方案 1: 检查输入文档

确保输入文档是有效的 `.docx` 文件（不是 `.doc`）。

在 Word 中打开输入文档，另存为 `.docx` 格式。

#### 方案 2: 使用 --verbose 查看错误

```bash
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

查看是否有错误信息。

#### 方案 3: 保留临时文件

```bash
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --keep-temp \
  --verbose
```

检查临时文件，看哪一步出错。

---

## 问题 8: MarkItDown docx 依赖缺失

### 症状

```
MissingDependencyException: DocxConverter recognized the input as a potential .docx file,
but the dependencies needed to read .docx files have not been installed.
```

或者：

```
✗ 错误：提取表格失败
  退出码: 1
```

### 原因

只安装了 `markitdown`，但没有安装处理 Word 文档所需的可选依赖 `markitdown[docx]`。

### 解决方案

安装完整的 MarkItDown docx 支持：

```bash
pip install markitdown[docx]
```

这会安装：
- `mammoth` - 用于读取 .docx 文件
- `lxml` - XML 解析库

**验证安装**：

```bash
python3 -c "import mammoth; print('✓ mammoth installed')"
```

**替代方案**：安装所有可选依赖

```bash
pip install markitdown[all]
```

---

## 问题 9: 新翻译文件格式不正确

### 症状

1. **低相似度警告很多**：
   ```
   ⚠️  警告：5 个配对的相似度较低（< 15%）
   ```

2. **输出文档包含多余字符**：
   Word 文档中出现表格边框符号 `│` 或行号

3. **翻译内容被截断**

### 原因

新翻译文件包含了不应该有的格式字符，例如：

**❌ 错误格式**：
```txt
│     1 誠摯邀請                                                             │
│     3 安麗事業的獨特之處，在於社群的凝聚力與人際連結...                      │
│       諮詢委員會領導人，正是每天將這份力量轉化為實際成果的中堅力量。您用行 │
```

问题：
- 包含表格边框 `│`
- 包含行號 `1`, `3`
- 包含多余的空格

### 解决方案

#### 方案 1: 清理新翻译文件（推荐）

**✓ 正确格式**：
```txt
誠摯邀請
安麗事業的獨特之處，在於社群的凝聚力與人際連結，而像您這樣的全球政策諮詢委員會領導人，正是每天將這份力量轉化為實際成果的中堅力量。您用行動向我們證明:團結一心、目標一致,就能攜手成就任何夢想。
我們誠摯期待2026年在義大利薩丁尼亞島——那令人驚嘆的翡翠海岸——與您相聚。
```

**要求**：
- ✅ 每行一个完整的翻译
- ✅ 不包含行号
- ✅ 不包含表格边框字符
- ✅ 不包含占位符行（如 `"<0/>"在第 <1/> 頁`）
- ✅ 翻译内容完整，不被截断

#### 方案 2: 使用清理脚本（推荐）

使用提供的清理脚本自动处理：

```bash
python3 ../scripts/clean_translation_text.py \
  new_translations.txt \
  new_translations_clean.txt \
  --verbose
```

脚本会自动：
- ✓ 删除表格边框字符 `│`
- ✓ 删除行号
- ✓ 删除多余空格
- ✓ 跳过空行
- ✓ 跳过占位符行
- ✓ 显示统计信息

输出示例：
```
统计:
  总行数: 17
  空行: 6
  占位符行: 1
  保留行数: 10
```

#### 方案 3: 手动使用 sed 清理

如果从 Word 或 Excel 复制的翻译，使用以下步骤手动清理：

1. **删除表格边框**：
   ```bash
   # 使用 sed 删除边框字符
   sed 's/│//g' new_translations.txt > cleaned.txt
   ```

2. **删除行号**：
   ```bash
   # 删除开头的数字和空格
   sed 's/^[ ]*[0-9][ ]*//g' cleaned.txt > final.txt
   ```

3. **删除多余空格**：
   ```bash
   # 删除行首和行尾空格
   sed 's/^[ ]*//g; s/[ ]*$//g' final.txt > new_translations_clean.txt
   ```

#### 方案 4: 检查完整性

**验证翻译是否完整**：

```bash
# 查看每行长度
awk '{print NR": "length($0)" chars"}' new_translations.txt

# 查看是否有截断（行尾是否有省略号）
grep '…$\|...$' new_translations.txt
```

**检查行数**：

运行映射生成时会显示：
```
✓ 过滤后保留 9 行（跳过了占位符行）
✓ 加载 17 个译文
```

如果新翻译行数 ≠ 过滤后的行数，说明：
- 新翻译包含了占位符
- 或新翻译行数不对

---

## 调试技巧

### 1. 总是使用 --verbose

```bash
--verbose
```

可以看到详细过程，帮助定位问题。

### 2. 分步执行

不要使用一键执行，分步执行可以更好地定位问题：

```bash
# 步骤 1
python3 ../scripts/extract_table_markitdown_simple.py \
  --input "input.docx" \
  --output "extracted_table.md"

# 检查 extracted_table.md 是否正确

# 步骤 2
python3 ../scripts/generate_translation_mapping.py \
  --markdown "extracted_table.md" \
  --new-translations "new_translations.txt" \
  --output "translations.json" \
  --match-by smart \
  --verbose

# 检查 translations.json 是否正确

# 步骤 3
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "Your Name" \
  --mode auto \
  --verbose
```

### 3. 使用诊断工具

遇到问题时，第一步总是运行诊断工具：

```bash
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "segment-id" \
  --verbose
```

### 4. 检查中间文件

查看生成的中间文件：
- `extracted_table.md` - 表格是否提取正确
- `translations.json` - 映射是否正确

### 5. 小批量测试

如果有大量翻译，先用少量翻译测试：
1. 只放 2-3 行翻译
2. 确认流程正确
3. 再处理全部翻译

---

## 常见错误代码

### 退出码 1

脚本执行失败。查看错误信息。

### FileNotFoundError

文件不存在。检查文件路径是否正确。

### KeyError: 'segment_id'

Markdown 表格格式不正确。检查表格是否包含 Segment ID 列。

### ValueError: Line count mismatch

行数不匹配。调整新翻译文件行数。

---

## 获取更多帮助

如果以上方案都无法解决问题，请提供：

1. **完整的命令**
   ```bash
   python3 ../scripts/run_complete_workflow.py ...（完整命令）
   ```

2. **错误信息**
   使用 `--verbose` 的完整输出

3. **相关文件**（如需要）
   - 输入文档（脱敏后）
   - 新翻译文件
   - 诊断工具输出

4. **环境信息**
   ```bash
   python --version
   pip list | grep -E "(markitdown|python-docx|lxml)"
   ```
