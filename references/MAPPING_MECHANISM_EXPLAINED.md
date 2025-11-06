# generate_translation_mapping.py 匹配机制详解

## 🔍 核心机制

`generate_translation_mapping.py` 提供**两种匹配方式**来生成对照表：

### 1. `--match-by segment_id` （默认，**顺序无关**）
### 2. `--match-by index` （**顺序必须一致**）

---

## 方式 1: `segment_id` 匹配（推荐，顺序无关）

### 工作原理

```python
# 核心代码
for idx, row in enumerate(old_table):
    segment_id = row['segment_id']
    old_text = row['target']

    if match_by == 'segment_id':
        new_text = new_translations.get(segment_id)  # 通过 segment_id 查找
```

**通过 segment_id 作为键来匹配，不依赖顺序！**

### 示例

**原始 Markdown 表格（过滤占位符后）：**
```markdown
| Segment ID | Target |
|------------|--------|
| 1360baf04e | PY26 已至... |
| 1460baf04e | 您是團隊的榜樣... |
| 1500986be2 | 聆聽 John Parker... |
```

**新翻译 JSON（顺序打乱也没关系）：**
```json
{
  "1500986be2": "請聆聽安麗市場事業總裁...",    ← 第3个
  "1360baf04e": "PY26 正式啟動！...",          ← 第1个
  "1460baf04e": "您是團隊的榜樣。為協助您..."  ← 第2个
}
```

**生成的对照表：**
```json
{
  "translations": [
    {
      "segment_id": "1360baf04e",
      "old_text": "PY26 已至...",
      "new_text": "PY26 正式啟動！..."  ← 正确匹配！
    },
    {
      "segment_id": "1460baf04e",
      "old_text": "您是團隊的榜樣...",
      "new_text": "您是團隊的榜樣。為協助您..."  ← 正确匹配！
    },
    {
      "segment_id": "1500986be2",
      "old_text": "聆聽 John Parker...",
      "new_text": "請聆聽安麗市場事業總裁..."  ← 正确匹配！
    }
  ]
}
```

### ✅ 优点
- **顺序无关**：新翻译可以是任意顺序
- **安全可靠**：通过 ID 精确匹配
- **灵活性高**：可以只更新部分翻译

### ❌ 缺点
- 需要新翻译文件是 **JSON 格式**
- 需要知道每个翻译对应的 segment_id

### 使用场景
- 从 AI 获得的翻译结果（可能顺序不同）
- 只需要更新部分段落
- 新翻译来自数据库或 API

### 命令示例

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.json \
  --output translations.json \
  --match-by segment_id \  # 默认值，可以省略
  --verbose
```

**新翻译文件格式（JSON）：**
```json
{
  "1360baf04e-73fb-432d-abf1-a0887de5f16a": "PY26 正式啟動！...",
  "1460baf04e-73fb-432d-abf1-a0887de5f16a": "您是團隊的榜樣。為協助您...",
  "1500986be2-218a-445e-8128-df72ccab7b69": "請聆聽安麗市場事業總裁..."
}
```

---

## 方式 2: `index` 匹配（**顺序必须一致**）

### 工作原理

```python
# 核心代码
for idx, row in enumerate(old_table):
    segment_id = row['segment_id']
    old_text = row['target']

    if match_by == 'index':
        new_text = new_translations.get(str(idx))  # 通过索引查找
```

**按行索引匹配，第1行对第1行，第2行对第2行，依此类推。**

### 示例

**原始 Markdown 表格（过滤占位符后）：**
```markdown
| 行号 | Segment ID | Target |
|------|------------|--------|
| 0    | 1360baf04e | PY26 已至... |
| 1    | 1460baf04e | 您是團隊的榜樣... |
| 2    | 1500986be2 | 聆聽 John Parker... |
```

**新翻译文本文件（必须按相同顺序）：**
```txt
PY26 正式啟動！作為創辦人理事會領袖...    ← 第0行，对应 1360baf04e
您是團隊的榜樣。為協助您更輕鬆...          ← 第1行，对应 1460baf04e
請聆聽安麗市場事業總裁 John Parker...    ← 第2行，对应 1500986be2
```

**内部处理：**
```python
new_translations = {
    "0": "PY26 正式啟動！...",
    "1": "您是團隊的榜樣。為協助您...",
    "2": "請聆聽安麗市場事業總裁..."
}

# 匹配过程：
# old_table[0] + new_translations["0"] -> 生成映射
# old_table[1] + new_translations["1"] -> 生成映射
# old_table[2] + new_translations["2"] -> 生成映射
```

**生成的对照表：**
```json
{
  "translations": [
    {
      "segment_id": "1360baf04e",
      "old_text": "PY26 已至...",
      "new_text": "PY26 正式啟動！..."  ← 正确匹配（索引0对0）
    },
    {
      "segment_id": "1460baf04e",
      "old_text": "您是團隊的榜樣...",
      "new_text": "您是團隊的榜樣。為協助您..."  ← 正确匹配（索引1对1）
    },
    {
      "segment_id": "1500986be2",
      "old_text": "聆聽 John Parker...",
      "new_text": "請聆聽安麗市場事業總裁..."  ← 正确匹配（索引2对2）
    }
  ]
}
```

### ⚠️ 如果顺序不一致会怎样？

**错误示例（顺序打乱）：**
```txt
請聆聽安麗市場事業總裁 John Parker...    ← 第0行
PY26 正式啟動！作為創辦人理事會領袖...    ← 第1行
您是團隊的榜樣。為協助您更輕鬆...          ← 第2行
```

**结果（错误的映射）：**
```json
{
  "translations": [
    {
      "segment_id": "1360baf04e",
      "old_text": "PY26 已至...",
      "new_text": "請聆聽安麗市場事業總裁..."  ← 错误！应该是 PY26
    },
    {
      "segment_id": "1460baf04e",
      "old_text": "您是團隊的榜樣...",
      "new_text": "PY26 正式啟動！..."  ← 错误！应该是"您是團隊"
    },
    {
      "segment_id": "1500986be2",
      "old_text": "聆聽 John Parker...",
      "new_text": "您是團隊的榜樣..."  ← 错误！应该是"請聆聽"
    }
  ]
}
```

### ✅ 优点
- **简单直接**：只需要一个文本文件，每行一个翻译
- **容易准备**：从 AI 复制粘贴即可
- **不需要 segment_id**：不用管 ID

### ❌ 缺点
- **顺序必须完全一致**：一旦顺序错了，所有映射都错
- **脆弱**：如果 Markdown 表格顺序改变，就会出错
- **难以调试**：不容易发现顺序错误

### 使用场景
- 新翻译来自纯文本（如 AI 对话）
- 确保新翻译的顺序与过滤后的表格完全一致
- 一次性全量更新所有翻译

### 命令示例

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --output translations.json \
  --match-by index \  # 必须指定
  --verbose
```

---

## 🎯 对比表

| 特性 | `segment_id` 匹配 | `index` 匹配 |
|------|------------------|-------------|
| **顺序依赖** | ❌ 顺序无关 | ✅ 必须一致 |
| **文件格式** | JSON | 文本或JSON |
| **需要 ID** | ✅ 需要 | ❌ 不需要 |
| **安全性** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **灵活性** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **易用性** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **部分更新** | ✅ 支持 | ❌ 不支持 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 📋 完整工作流程对比

### 使用 `segment_id` 匹配

```bash
# 步骤 1: 提取表格
python3 ../scripts/extract_table_markitdown_simple.py \
  --input input.docx \
  --output extracted_table.md

# 步骤 2: 准备新翻译 JSON
# 创建 new_translations.json:
{
  "1360baf04e-73fb-432d-abf1-a0887de5f16a": "PY26 正式啟動！...",
  "1460baf04e-73fb-432d-abf1-a0887de5f16a": "您是團隊的榜樣..."
}

# 步骤 3: 生成对照表（顺序无关）
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.json \
  --output translations.json \
  --match-by segment_id \
  --verbose

# 步骤 4: 应用翻译（使用默认作者 Claire.lee@amway.com）
python3 ../scripts/update_fc_insider_tracked.py \
  --input input.docx \
  --translations translations.json \
  --output output.docx \
  --mode read_inserted
```

### 使用 `index` 匹配

```bash
# 步骤 1: 提取表格
python3 ../scripts/extract_table_markitdown_simple.py \
  --input input.docx \
  --output extracted_table.md

# 步骤 2: 查看过滤后的行数
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations dummy.txt \
  --preview-only \
  --verbose
# 输出会显示：✓ 过滤后保留 13 行

# 步骤 3: 准备新翻译文本（必须正好 13 行，顺序一致）
# 创建 new_translations.txt:
PY26 正式啟動！...
您是團隊的榜樣...
請聆聽安麗市場事業總裁...
...（共13行）

# 步骤 4: 生成对照表（顺序必须一致）
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --output translations.json \
  --match-by index \
  --verbose

# 步骤 5: 应用翻译（使用默认作者 Claire.lee@amway.com）
python3 ../scripts/update_fc_insider_tracked.py \
  --input input.docx \
  --translations translations.json \
  --output output.docx \
  --mode read_inserted
```

---

## 🤔 我应该用哪种？

### 推荐：`segment_id` 匹配

**适合你的情况，如果：**
- ✅ 你可以从 AI 或工具获得带 segment_id 的 JSON
- ✅ 你想要更安全的匹配
- ✅ 你可能需要多次运行，只更新部分翻译
- ✅ 你不确定顺序是否完全一致

**如何准备 JSON：**

```python
# 简单的 Python 脚本生成 JSON
import json

# 从 Markdown 表格获取 segment_id
segment_ids = [
    "1360baf04e-73fb-432d-abf1-a0887de5f16a",
    "1460baf04e-73fb-432d-abf1-a0887de5f16a",
    "1500986be2-218a-445e-8128-df72ccab7b69",
    # ...
]

# 新翻译（可以是任意顺序）
new_texts = [
    "PY26 正式啟動！...",
    "您是團隊的榜樣。為協助您...",
    "請聆聽安麗市場事業總裁...",
    # ...
]

# 生成 JSON
translations = {sid: text for sid, text in zip(segment_ids, new_texts)}

with open('new_translations.json', 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)
```

### 可选：`index` 匹配

**适合你的情况，如果：**
- ✅ 你的新翻译来自纯文本（如 AI 对话）
- ✅ 你100%确定新翻译的顺序与过滤后的表格一致
- ✅ 你想要最简单的准备方式
- ⚠️ 但要非常小心顺序！

---

## ✅ 总结

1. **`segment_id` 匹配**：
   - 通过 segment_id 精确匹配
   - **顺序无关**，更安全
   - 需要 JSON 格式

2. **`index` 匹配**：
   - 按行索引匹配
   - **顺序必须完全一致**
   - 可以用纯文本

3. **推荐**：如果可能，尽量使用 `segment_id` 匹配方式

4. **注意**：无论哪种方式，都会自动过滤占位符行！

---

## 🔍 如何验证匹配是否正确

使用 `--preview-only` 先预览：

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.json \
  --match-by segment_id \
  --preview-only \
  --verbose
```

检查输出的变更预览，确认 old_text 和 new_text 是正确配对的！
