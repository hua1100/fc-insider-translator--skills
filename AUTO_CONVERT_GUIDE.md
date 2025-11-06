# 使用纯文本 + segment_id 匹配模式

## ✨ 新功能：自动转换

现在你可以**直接使用纯文本文件 + `--match-by segment_id`**！

脚本会自动将纯文本转换成 JSON 格式，享受 segment_id 匹配的安全性，同时保持纯文本的简便性！

---

## 🚀 快速开始（推荐方式）

### 步骤 1: 提取表格

```bash
python3 extract_table_markitdown_simple.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --output extracted_table.md
```

### 步骤 2: 准备新翻译（纯文本）

创建 `new_translations.txt`，每行一个翻译（**必须与过滤后的表格顺序一致**）：

```txt
PY26 正式啟動！作為創辦人理事會領袖，您在帶領團隊與事業邁向成功的過程中，扮演著舉足輕重的角色。
您是團隊的榜樣。為協助您更輕鬆且更有成就感地領導團隊，安麗今年推出了多項令人振奮的最新方案與優化措施。
請聆聽安麗市場事業總裁 John Parker 的開場致詞，為新績效年度揭開序幕。
接著，請繼續閱讀以下內容，了解如何在新年度開創佳績，其中包含獎勵提醒、培訓更新，以及 2026 年創辦人理事會的精彩預告。
全球獎勵認可（GAR）制度強化
感謝您的寶貴回饋與建議，GAR 現在比以往更完善。
我們深知，協助下線領袖成長需要時間、努力與全心投入，您理應因這份付出而獲得應有的肯定與獎勵。
因此，自今年起，白金資格者將可同時在寬度與深度上為您的 GAR 資格貢獻計算。
自雙鑽以上級別起，每一條白金腿可計入寬度統計。
白金下線資格者可為您貢獻 0.5 個資格積分（Qualification Credit）。
一條 Q6 白金腿（必須為 #1 或 #2 多重事業的下線）可計入雙鑽及以上級別的寬度要求。
Q6 白金資格者亦可貢獻至資格積分（QC）統計。
如需進一步資訊，請洽您的市場聯絡窗口。
```

**重要**：
- 不要包含占位符行（如 `"<0/>"在第 <1/> 頁`）
- 行数必须与过滤后的表格行数一致

### 步骤 3: 生成对照表（使用 segment_id 匹配）

```bash
python3 generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --output translations.json \
  --match-by segment_id \
  --verbose
```

**关键**：使用 `--match-by segment_id` 而不是 `index`！

### 预期输出

```
================================================================================
生成翻译对照表
================================================================================

读取 Markdown 表格: extracted_table.md
✓ 加载 26 行

占位符过滤:
  总行数: 26
  保留: 13
  跳过: 13

跳过的占位符行（前10个）:
    1. 10ad6613a-8149-4c02-9b21-019c8421d195: "<0/>"在第 <1/> 頁
    2. 24efa4ea5-2ff1-449b-8453-04c7d9efd9ae: "<2/>"
    ...

✓ 过滤后保留 13 行（跳过了占位符行）

读取新译文: new_translations.txt
✓ 加载 13 个译文

🔄 检测到纯文本格式 + segment_id 匹配模式
   自动将文本转换为 JSON 格式（文本行 → segment_id）...
✓ 转换完成：13 个译文已映射到 segment_id

转换示例（前3个）:
  1. 1360baf04e-73fb-432d-abf1-a0887de5f16a: PY26 正式啟動！作為創辦人理事會領袖，您在帶領團隊與事業...
  2. 1460baf04e-73fb-432d-abf1-a0887de5f16a: 您是團隊的榜樣。為協助您更輕鬆且更有成就感地領導團隊...
  3. 1500986be2-218a-445e-8128-df72ccab7b69: 請聆聽安麗市場事業總裁 John Parker 的開場致詞...

生成对照表（匹配方式: segment_id）...
✓ 生成 13 个变更

✓ 验证通过

================================================================================
变更预览（前 10 个，共 13 个）
================================================================================

[1] 1360baf04e-73fb-432d-abf1-a0887de5f16a
  旧: PY26 已至，作為全球政策諮詢委員領導者，您在助力團隊與事業實現本年度成功的過程中扮演著關鍵角色。
  新: PY26 正式啟動！作為創辦人理事會領袖，您在帶領團隊與事業邁向成功的過程中，扮演著舉足輕重的角色。

[2] 1460baf04e-73fb-432d-abf1-a0887de5f16a
  旧: 您是團隊的榜樣，而 Amway 也準備了令人振奮的更新與最佳化，讓團隊領導工作更輕鬆、獎勵更豐厚。
  新: 您是團隊的榜樣。為協助您更輕鬆且更有成就感地領導團隊，安麗今年推出了多項令人振奮的最新方案與優化措施。

...

✓ 对照表已保存: translations.json
```

### 步骤 4: 应用翻译

```bash
python3 update_fc_insider_tracked.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --translations translations.json \
  --output "/Users/hua/md腳本/output_final.docx" \
  --author "Gemini" \
  --mode read_inserted \
  --verbose
```

---

## 🎯 工作原理

### 自动转换过程

```
1️⃣ 读取纯文本新翻译
   new_translations.txt (13行) → {"0": "第1行", "1": "第2行", ...}

2️⃣ 读取并过滤 Markdown 表格
   extracted_table.md (26行) → 过滤后 13行

3️⃣ 检测到 text 格式 + segment_id 匹配
   🔄 自动转换模式启动！

4️⃣ 按索引将文本与 segment_id 配对
   第0行文本 → segment_id[0] → "1360baf04e..."
   第1行文本 → segment_id[1] → "1460baf04e..."
   第2行文本 → segment_id[2] → "1500986be2..."
   ...

5️⃣ 生成 JSON 格式映射
   {
     "1360baf04e...": "PY26 正式啟動！...",
     "1460baf04e...": "您是團隊的榜樣...",
     "1500986be2...": "請聆聽安麗市場事業總裁..."
   }

6️⃣ 使用 segment_id 进行匹配
   通过 segment_id 精确匹配，安全可靠！
```

---

## ✅ 优势

现在你可以享受**两种方式的优点**：

| 特性 | 传统 `index` 匹配 | 传统 `segment_id` 匹配 | **新方式（自动转换）** |
|------|-----------------|---------------------|---------------------|
| **文件格式** | 纯文本 | JSON | **纯文本** ✅ |
| **准备难度** | 简单 | 复杂 | **简单** ✅ |
| **匹配方式** | 索引 | segment_id | **segment_id** ✅ |
| **安全性** | ⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** ✅ |
| **顺序依赖** | 严格 | 无关 | 初始需要，转换后无关 |

**最佳选择**：简单 + 安全 + 可靠！

---

## ⚠️ 重要注意事项

### 1. 新翻译行数必须匹配

脚本会自动检查：

```
⚠️  警告：
   新翻译行数: 15
   过滤后表格行数: 13
   ✗ 新翻译行数不足！请检查新翻译文件
```

**解决方法**：
- 检查你的新翻译文件
- 确保没有包含占位符行
- 确保行数与过滤后的表格一致

### 2. 初始顺序仍然重要

虽然使用 segment_id 匹配，但在**自动转换阶段**，文本行的顺序仍然需要与过滤后的表格一致。

转换后，生成的 JSON 就可以乱序了（但你不需要手动处理 JSON）。

### 3. 使用 `--verbose` 验证

使用 `--verbose` 可以看到转换示例：

```
转换示例（前3个）:
  1. 1360baf04e...: PY26 正式啟動！...
  2. 1460baf04e...: 您是團隊的榜樣...
  3. 1500986be2...: 請聆聽安麗市場事業總裁...
```

检查这些配对是否正确！

---

## 🆚 三种使用方式对比

### 方式 1: 纯文本 + index 匹配（不推荐）

```bash
python3 generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --match-by index
```

- ❌ 匹配方式不安全
- ✅ 文件准备简单

### 方式 2: JSON + segment_id 匹配（安全但复杂）

```bash
python3 generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.json \
  --match-by segment_id
```

- ✅ 匹配方式安全
- ❌ 需要手动准备 JSON

### 方式 3: 纯文本 + segment_id 匹配 + 自动转换（**推荐** ⭐）

```bash
python3 generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --match-by segment_id \  # 关键！使用 segment_id
  --verbose
```

- ✅ 匹配方式安全
- ✅ 文件准备简单
- ✅ 自动转换，最佳选择！

---

## 📋 完整工作流程示例

```bash
# 1. 提取表格
python3 extract_table_markitdown_simple.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --output extracted_table.md

# 2. 准备新翻译文本文件（13行，不含占位符）
# 创建 new_translations.txt

# 3. 生成对照表（自动转换模式）
python3 generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --output translations.json \
  --match-by segment_id \
  --verbose

# 4. 检查预览输出，确认映射正确

# 5. 应用翻译
python3 update_fc_insider_tracked.py \
  --input "/Users/hua/md腳本/FCInsider_Dec2025_Issue9_翻譯修訂版.docx" \
  --translations translations.json \
  --output "/Users/hua/md腳本/output_final.docx" \
  --author "Gemini" \
  --mode read_inserted \
  --verbose
```

---

## ❓ FAQ

### Q: 我还需要手动创建 JSON 吗？

**A**: 不需要！使用 `--match-by segment_id` + 纯文本文件，脚本会自动转换。

### Q: 自动转换后的匹配还安全吗？

**A**: 是的！转换后使用的是 segment_id 匹配，和手动 JSON 一样安全。

### Q: 如果行数不匹配怎么办？

**A**: 脚本会提示错误并停止。检查你的新翻译文件，确保：
- 不包含占位符行
- 行数与过滤后的表格一致

### Q: 我怎么知道过滤后有多少行？

**A**: 运行脚本时会显示：
```
✓ 过滤后保留 13 行（跳过了占位符行）
```

你的新翻译文件应该正好有 13 行。

---

## ✅ 总结

1. **准备纯文本**：每行一个翻译，不含占位符
2. **使用 segment_id 匹配**：`--match-by segment_id`
3. **自动转换**：脚本自动将文本转换成 JSON
4. **安全匹配**：享受 segment_id 匹配的安全性

**这是最简单、最安全的方式！** 🎉
