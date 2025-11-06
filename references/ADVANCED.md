# 高级功能详解

深入了解核心功能的工作原理和高级用法。

---

## 智能匹配

使用文本相似度算法自动配对新旧翻译，即使顺序完全不一致也能正确匹配。

### 工作原理

#### 1. 相似度计算

综合使用三种方法计算相似度：

```python
def calculate_text_similarity(text1: str, text2: str) -> float:
    # 1. 序列相似度 (权重 50%)
    seq_ratio = SequenceMatcher(None, text1, text2).ratio()

    # 2. 共同字符比例 (权重 20%)
    set1, set2 = set(text1), set(text2)
    char_ratio = len(set1 & set2) / max(len(set1), len(set2))

    # 3. 词汇重叠度 (权重 30%)
    words1 = set(re.findall(r'[\w]+', text1))
    words2 = set(re.findall(r'[\w]+', text2))
    word_ratio = len(words1 & words2) / max(len(words1), len(words2))

    # 加权综合
    return (seq_ratio * 0.5) + (char_ratio * 0.2) + (word_ratio * 0.3)
```

**示例**：
```
文本1: "PY26 已至，作為全球政策諮詢委員領導者..."
文本2: "PY26 正式啟動！作為創辦人理事會領袖..."

序列相似度: 0.75 (字符序列匹配)
共同字符: 0.82 (共有字符比例)
词汇重叠: 0.68 (共同词汇)

最终相似度: 0.75 * 0.5 + 0.82 * 0.2 + 0.68 * 0.3 = 87.34%
```

#### 2. 贪婪匹配算法

```python
def smart_match_translations(old_table, new_texts, min_similarity=0.15):
    # 步骤 1: 计算所有可能配对的相似度
    pairings = []
    for i, old_row in enumerate(old_table):
        for j, new_text in enumerate(new_texts):
            similarity = calculate_text_similarity(old_row['target'], new_text)
            pairings.append((similarity, i, j))

    # 步骤 2: 按相似度从高到低排序
    pairings.sort(reverse=True, key=lambda x: x[0])

    # 步骤 3: 贪婪选择最佳配对
    used_old = set()
    used_new = set()
    matches = {}

    for similarity, old_idx, new_idx in pairings:
        if old_idx not in used_old and new_idx not in used_new:
            matches[old_idx] = (new_idx, similarity)
            used_old.add(old_idx)
            used_new.add(new_idx)

    return matches
```

**工作流程**：
```
1. 计算所有可能配对:
   旧翻译1 vs 新翻译1: 45%
   旧翻译1 vs 新翻译2: 87%  ← 最高
   旧翻译1 vs 新翻译3: 23%
   旧翻译2 vs 新翻译1: 82%  ← 次高
   ...

2. 排序:
   (87%, 旧1, 新2)
   (82%, 旧2, 新1)
   (75%, 旧3, 新3)
   ...

3. 贪婪选择:
   第1轮: 选择 (87%, 旧1, 新2) → 旧1和新2标记为已使用
   第2轮: 选择 (82%, 旧2, 新1) → 旧2和新1标记为已使用
   第3轮: 选择 (75%, 旧3, 新3) → 旧3和新3标记为已使用
   ...
```

### 相似度阈值

默认最小相似度阈值：**15%**

**低于阈值时会警告**：
```
⚠️ 警告：2 个配对的相似度较低（< 15%）
   建议检查这些配对是否正确
```

**调整阈值**：

编辑 `generate_translation_mapping.py`：
```python
new_translations = smart_match_translations(
    old_table,
    text_list,
    min_similarity=0.20,  # 提高到 20%
    verbose=args.verbose
)
```

- **提高阈值**（如 0.30）：更严格，只接受高相似度配对
- **降低阈值**（如 0.10）：更宽松，接受更多配对

### 适用场景

✅ **最适合**：
- 新翻译顺序与表格不一致
- 翻译风格有较大变化但内容相关
- 不确定顺序是否正确

❌ **不适合**：
- 完全不相关的文本（相似度会很低）
- 高度重复的文本（难以区分）

---

## 占位符自动过滤

自动识别并跳过占位符行，避免错误配对。

### 识别规则

```python
def is_placeholder_row(text: str) -> bool:
    # 规则 1: 移除占位符和常见词后，剩余内容很少
    without_placeholders = re.sub(r'[<"]?\d+/?[>"]?', '', text)
    without_placeholders = re.sub(r'["""\'\'<>]', '', without_placeholders)
    without_placeholders = re.sub(r'(在第|頁|on page|page)', '', without_placeholders, flags=re.IGNORECASE)

    if len(without_placeholders.strip()) <= 3:
        return True

    # 规则 2: 包含多个占位符且文本很短
    placeholder_count = len(re.findall(r'<\d+/>', text))
    if placeholder_count >= 2 and len(text) <= 30:
        return True

    return False
```

### 识别示例

✅ **会被过滤的占位符行**：
```
"<0/>"在第 <1/> 頁        → 是占位符
"<2/>"                     → 是占位符
第 <12/> 頁                → 是占位符
內文                        → 是占位符（太短）
<0/> on page <1/>          → 是占位符
```

❌ **不会被过滤的实际内容**：
```
PY26 正式啟動！作為創辦人理事會領袖...  → 不是占位符
您是團隊的榜樣。為協助您更輕鬆且...      → 不是占位符
請聆聽安麗市場事業總裁 John Parker... → 不是占位符
```

### 过滤过程

```
原始表格: 26 行
  ↓
应用过滤规则
  ↓
占位符行: 13 行 (跳过)
├─ "<0/>"在第 <1/> 頁
├─ "<2/>"
├─ 第 <12/> 頁
├─ 內文
└─ ...
  ↓
保留行: 13 行 (用于匹配)
├─ PY26 正式啟動！...
├─ 您是團隊的榜樣...
└─ ...
```

### 禁用过滤（不推荐）

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json" \
  --skip-placeholder-filter  # 不推荐
```

---

## 追踪修订处理

自动检测和处理已有追踪修订的 Word 文档。

### 问题背景

python-docx 的限制：
```python
# 普通文本可以读取
for run in paragraph.runs:
    text = run.text  # ✓ 可以读取

# 追踪修订中的文本无法读取
# <w:del><w:r><w:delText>文本</w:delText></w:r></w:del>
for run in paragraph.runs:
    text = run.text  # ✗ runs 为空，无法读取
```

### 解决方案：直接解析 XML

```python
def get_cell_text_from_tracked_changes(cell, mode='auto'):
    text_parts = []

    for paragraph in cell.paragraphs:
        para_element = paragraph._element

        if mode == 'read_deleted' or mode == 'auto':
            # 读取 <w:delText>
            del_elements = para_element.findall(qn('w:del'))
            for del_elem in del_elements:
                del_texts = del_elem.findall('.//' + qn('w:delText'))
                for del_text in del_texts:
                    if del_text.text:
                        text_parts.append(del_text.text)

        if mode == 'read_inserted' or mode == 'auto':
            # 读取 <w:ins> 中的 <w:t>
            ins_elements = para_element.findall(qn('w:ins'))
            for ins_elem in ins_elements:
                ins_texts = ins_elem.findall('.//' + qn('w:t'))
                for ins_text in ins_texts:
                    if ins_text.text:
                        text_parts.append(ins_text.text)

    return ''.join(text_parts)
```

### 三种读取模式

#### auto（自动检测）

```python
def auto_detect_text_source(cell):
    # 1. 检查是否有删除的文本
    deleted_text = get_cell_text_from_tracked_changes(cell, 'read_deleted')
    if deleted_text:
        return 'deleted', deleted_text

    # 2. 检查是否有插入的文本
    inserted_text = get_cell_text_from_tracked_changes(cell, 'read_inserted')
    if inserted_text:
        return 'inserted', inserted_text

    # 3. 读取普通文本
    normal_text = get_cell_text_normal(cell)
    return 'normal', normal_text
```

**决策树**：
```
检查单元格
  ↓
有 <w:del> 吗？
  ↓ 是
  读取 <w:delText>
  ↓
  返回 deleted

  ↓ 否
有 <w:ins> 吗？
  ↓ 是
  读取 <w:ins> 中的 <w:t>
  ↓
  返回 inserted

  ↓ 否
读取普通 runs
  ↓
  返回 normal
```

#### read_deleted

强制从删除的文本读取（`<w:delText>`）。

**适用场景**：
- 文档已有追踪修订
- 旧翻译在删除的文本中
- auto 模式选择了错误的来源

#### read_inserted

强制从插入的文本读取（`<w:ins>` 中的 `<w:t>`）。

**适用场景**：
- 文档已有追踪修订
- 旧翻译在插入的文本中
- auto 模式选择了错误的来源

### 清除并重新应用

```python
def clear_and_apply_tracked_change(cell, old_text, new_text, author):
    # 步骤 1: 清除单元格所有内容
    for paragraph in cell.paragraphs:
        paragraph.clear()

    # 步骤 2: 添加删除的旧文本
    para = cell.paragraphs[0]
    del_run = para._element.add_w_del()
    del_run.set(qn('w:author'), author)
    del_run.set(qn('w:date'), datetime.now().isoformat())

    del_r = del_run.add_w_r()
    del_text = del_r.add_w_delText()
    del_text.text = old_text

    # 步骤 3: 添加插入的新文本
    ins_run = para._element.add_w_ins()
    ins_run.set(qn('w:author'), author)
    ins_run.set(qn('w:date'), datetime.now().isoformat())

    ins_r = ins_run.add_w_r()
    ins_text = ins_r.add_w_t()
    ins_text.text = new_text
```

**效果**：
```xml
<!-- 应用后的 XML 结构 -->
<w:p>
  <w:del w:author="Gemini" w:date="2025-01-06T10:30:00">
    <w:r>
      <w:delText>PY26 已至，作為全球政策諮詢委員...</w:delText>
    </w:r>
  </w:del>
  <w:ins w:author="Gemini" w:date="2025-01-06T10:30:00">
    <w:r>
      <w:t>PY26 正式啟動！作為創辦人理事會...</w:t>
    </w:r>
  </w:ins>
</w:p>
```

**在 Word 中显示**：
```
PY26 已至，作為全球政策諮詢委員...  ← 红色删除线
PY26 正式啟動！作為創辦人理事會...  ← 红色下划线
```

---

## 诊断工具

深度分析 Word 文档结构，识别问题，提供解决方案建议。

### 分析内容

```python
def analyze_cell_deep(cell):
    analysis = {
        'runs': [],
        'total_chars': 0,
        'has_tracked_changes': False,
        'xml_structure': ''
    }

    # 1. 分析 runs
    for run in cell.paragraphs[0].runs:
        run_info = {
            'text': run.text,
            'style': run.style.name if run.style else None,
            'bold': run.bold,
            'italic': run.italic,
            'font_name': run.font.name,
            'font_size': run.font.size
        }
        analysis['runs'].append(run_info)

    # 2. 检查追踪修订
    para_element = cell.paragraphs[0]._element
    if para_element.findall(qn('w:del')) or para_element.findall(qn('w:ins')):
        analysis['has_tracked_changes'] = True

    # 3. 导出 XML
    analysis['xml_structure'] = etree.tostring(
        para_element,
        encoding='unicode',
        pretty_print=True
    )

    return analysis
```

### 自动建议

```python
def generate_solution_recommendation(analysis):
    if analysis['has_tracked_changes']:
        return """
        推荐解决方案:
          → 使用 update_fc_insider_tracked.py
          → 模式: auto（自动检测）
          → 或根据 XML 结构选择 read_deleted/read_inserted
        """

    if len(analysis['runs']) == 0:
        return """
        问题: 无法读取 runs
        可能原因: 追踪修订或特殊格式
        建议: 使用 update_fc_insider_tracked.py
        """

    return """
    推荐解决方案:
      → 使用 update_fc_insider_simple.py
      → 文档结构正常
    """
```

### 使用示例

```bash
# 基本分析
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "1360baf04e-73fb-432d-abf1-a0887de5f16a" \
  --verbose

# 导出 XML 和 JSON
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "1360baf04e-73fb-432d-abf1-a0887de5f16a" \
  --export-xml \
  --export-json "analysis.json" \
  --verbose
```

---

## 自动文本转 JSON

使用纯文本 + segment_id 匹配时，自动将文本转换为 JSON 格式。

### 工作原理

```python
def auto_convert_text_to_json(text_dict, old_table):
    """
    将纯文本转换为 segment_id 映射

    text_dict: {"0": "第1行", "1": "第2行", ...}
    old_table: [{"segment_id": "abc", ...}, ...]

    返回: {"abc": "第1行", "def": "第2行", ...}
    """
    json_dict = {}

    for idx, row in enumerate(old_table):
        segment_id = row['segment_id']
        text = text_dict.get(str(idx))

        if text:
            json_dict[segment_id] = text

    return json_dict
```

### 使用示例

```bash
# 纯文本文件 + segment_id 匹配
python3 ../scripts/generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \  # 纯文本！
  --output "translations.json" \
  --match-by segment_id \  # segment_id 匹配！
  --verbose
```

**输出**：
```
🔄 检测到纯文本格式 + segment_id 匹配模式
   自动将文本转换为 JSON 格式（文本行 → segment_id）...
✓ 转换完成：13 个译文已映射到 segment_id

转换示例（前3个）:
  1. 1360baf04e...: PY26 正式啟動！...
  2. 1460baf04e...: 您是團隊的榜樣...
  3. 1500986be2...: 請聆聽安麗市場事業總裁...
```

---

## 自定义相似度算法

如果默认的相似度算法不适合你的场景，可以自定义。

### 修改权重

编辑 `generate_translation_mapping.py`：

```python
def calculate_text_similarity(text1: str, text2: str) -> float:
    seq_ratio = SequenceMatcher(None, text1, text2).ratio()

    set1, set2 = set(text1), set(text2)
    char_ratio = len(set1 & set2) / max(len(set1), len(set2)) if set1 and set2 else 0

    words1 = set(re.findall(r'[\w]+', text1))
    words2 = set(re.findall(r'[\w]+', text2))
    word_ratio = len(words1 & words2) / max(len(words1), len(words2)) if words1 and words2 else 0

    # 调整权重
    # 默认: 0.5, 0.2, 0.3
    # 更注重序列: 0.7, 0.15, 0.15
    # 更注重词汇: 0.3, 0.2, 0.5
    return (seq_ratio * 0.5) + (char_ratio * 0.2) + (word_ratio * 0.3)
```

### 添加新的相似度方法

```python
def calculate_text_similarity_custom(text1: str, text2: str) -> float:
    # 方法 1-3: 现有方法
    ...

    # 方法 4: 自定义方法（例如：长度相似度）
    len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))

    # 综合
    return (seq_ratio * 0.4) + (char_ratio * 0.2) + (word_ratio * 0.3) + (len_ratio * 0.1)
```

---

## 总结

掌握这些高级功能，可以处理更复杂的场景：

- **智能匹配** - 处理顺序不一致
- **占位符过滤** - 自动跳过无用行
- **追踪修订处理** - 处理已有修订的文档
- **诊断工具** - 快速定位问题
- **自动转换** - 简化文件准备

根据实际需求选择合适的功能和参数！
