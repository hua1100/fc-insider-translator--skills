# 占位符过滤问题解决方案

## 🔍 问题描述

在使用 `generate_translation_mapping.py` 生成翻译映射时，脚本错误地将占位符行（如 `"<0/>"在第 <1/> 頁`）当作需要翻译的内容，导致映射完全错乱。

**错误的映射示例**：
```json
{
  "segment_id": "10ad6613a-8149-4c02-9b21-019c8421d195",
  "old_text": ""<0/>"在第 <1/> 頁",  ← 这是占位符，不应该被翻译
  "new_text": "PY26 正式啟動！..."      ← 错误地分配了新翻译
}
```

---

## ✅ 解决方案

已更新 `generate_translation_mapping.py`，添加了**自动占位符过滤**功能。

### 新功能

1. **自动识别占位符行**：
   - `"<0/>"在第 <1/> 頁`
   - `"<2/>"`
   - `<6/> 在第 <7/> 頁`
   - `第 <12/> 頁`
   - 等等

2. **智能过滤算法**：
   - 移除占位符标记后，如果剩余内容少于3个字符，判定为占位符行
   - 如果包含2个或更多占位符且总长度很短，判定为占位符行
   - 支持中文和英文占位符模式

3. **详细输出**：
   - 显示过滤前后的行数
   - 使用 `--verbose` 可以看到哪些行被跳过了

---

## 🚀 使用方法

### 基本用法（推荐）

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --output translations.json \
  --match-by index \
  --verbose
```

**关键参数**：
- `--verbose` - 显示占位符过滤的详细信息
- `--match-by index` - 使用行索引匹配（适合纯文本新翻译）

### 输出示例

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
    3. 3d803cfca-abf7-46be-96d3-f8d4834e03a7: "<3/>"在第 <4/> 頁
    4. 4256ee1e1-0855-45a1-8972-8b5b1eb5918c: "<5/>"
    5. 526e4cc51-2d9b-4451-b21c-f6ed165318dc: <6/> 在第 <7/> 頁
    ...

✓ 过滤后保留 13 行（跳过了占位符行）

读取新译文: new_translations.txt
✓ 加载 13 个译文

生成对照表（匹配方式: index）...
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

... ← 现在映射正确了！
```

---

## 📋 完整工作流程

### 步骤 1: 准备新翻译文本文件

创建 `new_translations.txt`，每行一个翻译（**只包含需要翻译的内容，不包括占位符**）：

```
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

### 步骤 2: 运行生成脚本

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --output translations.json \
  --match-by index \
  --verbose
```

### 步骤 3: 检查输出

脚本会显示：
- 过滤了多少占位符行
- 保留了多少真实翻译行
- 生成了多少个变更
- 前10个变更的预览

### 步骤 4: 应用翻译

使用生成的 `translations.json` 更新 Word 文档：

```bash
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations translations.json \
  --output "output.docx" \
  --mode read_inserted \
  --verbose
```

**提示**：默认作者为 `Claire.lee@amway.com`，可以省略 `--author` 参数。

---

## 🔧 高级选项

### 跳过占位符过滤

如果你想保留占位符行（不推荐），可以使用：

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --output translations.json \
  --skip-placeholder-filter  ← 跳过过滤
```

### 预览模式

只预览而不保存文件：

```bash
python3 ../scripts/generate_translation_mapping.py \
  --markdown extracted_table.md \
  --new-translations new_translations.txt \
  --preview-only \
  --verbose
```

---

## 🐛 故障排查

### 问题 1: 过滤了太多行

**症状**：脚本过滤掉了一些你想保留的行

**解决方案**：
1. 使用 `--verbose` 查看哪些行被过滤了
2. 如果确实需要这些行，使用 `--skip-placeholder-filter` 跳过过滤
3. 或者修改 `is_placeholder_row()` 函数的判断逻辑

### 问题 2: 行数不匹配

**症状**：过滤后的行数与新翻译的数量不匹配

```
✓ 过滤后保留 13 行
✓ 加载 15 个译文  ← 数量不匹配！
```

**解决方案**：
1. 检查新翻译文件，确保每行对应一个真实的翻译（不包括占位符）
2. 使用 `--verbose` 查看哪些行被过滤了
3. 调整新翻译文件，使行数匹配

### 问题 3: 映射还是不正确

**症状**：即使过滤了占位符，映射还是不对

**解决方案**：
1. 使用 `--preview-only --verbose` 查看详细的预览
2. 检查 Markdown 表格的顺序是否正确
3. 确认新翻译文件的顺序与过滤后的表格顺序一致
4. 考虑使用 `--match-by segment_id` 而不是 `index`（需要新翻译文件是 JSON 格式）

---

## 📚 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--markdown` | Markdown 表格文件路径 | **必需** |
| `--new-translations` | 新翻译文件路径 | **必需** |
| `--output` | 输出 JSON 文件路径 | `translations.json` |
| `--match-by` | 匹配方式（`segment_id` 或 `index`） | `segment_id` |
| `--format` | 新翻译格式（`json`, `text`, `auto`） | `auto` |
| `--preview-only` | 只预览，不保存 | `False` |
| `--skip-placeholder-filter` | 跳过占位符过滤 | `False` |
| `--verbose` | 显示详细信息 | `False` |

---

## ✅ 总结

1. **问题根源**：占位符行被当作需要翻译的内容
2. **解决方案**：自动过滤占位符行
3. **推荐用法**：使用 `--match-by index --verbose`
4. **验证方法**：使用 `--preview-only` 先预览再保存

现在重新运行生成脚本，应该可以得到正确的映射了！🎯
