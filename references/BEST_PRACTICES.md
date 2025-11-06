# 使用最佳实践

掌握这些最佳实践，让翻译更新工作更高效、更可靠。

---

## 推荐工作流程

### 首次使用：分步执行

第一次使用时，建议分步执行以了解每个步骤：

```bash
# 步骤 1: 提取表格
python3 ../scripts/extract_table_markitdown_simple.py \
  --input "input.docx" \
  --output "extracted_table.md"

# 📝 检查 extracted_table.md，确认表格提取正确

# 步骤 2: 生成翻译映射（智能匹配）
python3 ../scripts/generate_translation_mapping.py \
  --markdown "extracted_table.md" \
  --new-translations "new_translations.txt" \
  --output "translations.json" \
  --match-by smart \
  --verbose

# 📝 检查输出的匹配示例和相似度分数

# 步骤 3: 应用翻译
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "Your Name" \
  --mode auto \
  --verbose

# 📝 在 Word 中打开 output.docx，确认追踪修订正确
```

### 熟悉后：一键执行

熟悉流程后，使用一键执行：

```bash
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

---

## 匹配方式选择

### 推荐：smart 智能匹配 ⭐⭐⭐⭐⭐

**始终使用智能匹配，除非有特殊原因。**

```bash
--match-by smart --verbose
```

**优势**：
- ✅ 顺序无关，不用担心顺序问题
- ✅ 自动配对，省时省力
- ✅ 显示相似度，心里有底
- ✅ 容错能力强，即使翻译风格变化也能匹配

**示例输出**：
```
匹配示例（按相似度排序）:
  1. 相似度: 87.34%  ← 高相似度，可信
     旧: PY26 已至，作為全球政策諮詢委員...
     新: PY26 正式啟動！作為創辦人理事會...
```

### 不推荐：index 索引匹配 ⚠️

**只在100%确定顺序一致时使用。**

```bash
--match-by index  # 不推荐
```

**缺点**：
- ❌ 顺序必须完全一致
- ❌ 顺序错了就全错
- ❌ 难以发现问题

---

## 参数使用建议

### 1. 总是使用 --verbose ✅

**推荐**：
```bash
--verbose
```

**原因**：
- 查看详细过程
- 了解匹配结果
- 发现潜在问题
- 调试错误更容易

### 2. 使用 auto 模式 ✅

**推荐**：
```bash
--mode auto
```

**原因**：
- 自动检测文档类型
- 适合大多数情况
- 省去手动判断

只有当 auto 模式失败时，才手动指定模式。

### 3. 指定有意义的作者名 ✅

**推荐**：
```bash
--author "Gemini" 或 --author "Claude"
```

**不推荐**：
```bash
--author "Translator"  # 太通用
```

**原因**：
- 在 Word 中查看修订时，能清楚知道是哪个翻译引擎的结果
- 便于对比不同翻译引擎的效果

---

## 文件准备建议

### 新翻译文件

#### ✅ 推荐格式：纯文本

```txt
PY26 正式啟動！作為創辦人理事會領袖...
您是團隊的榜樣。為協助您更輕鬆且...
請聆聽安麗市場事業總裁 John Parker...
```

**优点**：
- 简单直接
- 容易准备
- 配合 smart 匹配，顺序无关

#### ❌ 不要包含占位符

**错误示例**：
```txt
PY26 正式啟動！作為創辦人理事會領袖...
"<0/>"在第 <1/> 頁  ← 不要包含这种行！
您是團隊的榜樣。為協助您更輕鬆且...
```

**正确示例**：
```txt
PY26 正式啟動！作為創辦人理事會領袖...
您是團隊的榜樣。為協助您更輕鬆且...
```

#### ✅ 确保行数正确

运行脚本时会显示：
```
✓ 过滤后保留 13 行（跳过了占位符行）
```

你的新翻译文件应该正好有 **13 行**。

---

## 检查与验证

### 1. 检查匹配结果

生成映射表后，查看输出的匹配示例：

```
匹配示例（按相似度排序）:
  1. 相似度: 87.34%
     旧: PY26 已至，作為全球政策諮詢委員...
     新: PY26 正式啟動！作為創辦人理事會...  ← 检查是否正确配对
```

**关注点**：
- 相似度是否合理（通常 > 70%）
- 配对是否正确
- 是否有低相似度警告

### 2. 检查变更预览

```
================================================================================
变更预览（前 10 个，共 13 个）
================================================================================

[1] 1360baf04e-73fb-432d-abf1-a0887de5f16a
  旧: PY26 已至，作為全球政策諮詢委員...
  新: PY26 正式啟動！作為創辦人理事會...  ← 检查是否正确

[2] 1460baf04e-73fb-432d-abf1-a0887de5f16a
  旧: 您是團隊的榜樣，而 Amway 也準備了...
  新: 您是團隊的榜樣。為協助您更輕鬆且...  ← 检查是否正确
```

**如果发现配对错误**，停止流程，调整新翻译文件或使用其他匹配方式。

### 3. 在 Word 中验证

应用翻译后，在 Word 中打开输出文档：

1. **启用"追踪修订"视图**
   - 审阅 → 追踪修订 → 显示标记

2. **检查修订**
   - 删除的文本（红色删除线）是否是旧翻译
   - 插入的文本（红色下划线）是否是新翻译

3. **接受或拒绝修订**
   - 审阅 → 接受 → 接受所有修订

---

## 小批量测试策略

处理大量翻译时，先小批量测试：

### 步骤 1: 准备测试文件

```txt
# test_translations.txt（只放 2-3 行）
PY26 正式啟動！作為創辦人理事會領袖...
您是團隊的榜樣。為協助您更輕鬆且...
```

### 步骤 2: 测试流程

```bash
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "test_translations.txt" \
  --output "test_output.docx" \
  --author "Your Name" \
  --verbose
```

### 步骤 3: 验证结果

在 Word 中打开 `test_output.docx`，确认：
- 配对正确
- 追踪修订正确
- 没有错误

### 步骤 4: 处理全部

确认无误后，处理全部翻译：

```bash
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "all_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

---

## 版本控制建议

### 保留输入文件

```bash
# 使用日期或版本号
input_20250106.docx
new_translations_20250106.txt
output_20250106.docx
```

### 保留中间文件（可选）

```bash
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --keep-temp \
  --verbose
```

保留的临时文件：
- `extracted_table.md` - 提取的表格
- `translations.json` - 翻译映射

可以用于调试或重新应用。

---

## 处理不同场景

### 场景 1: 新翻译顺序与表格不一致

**解决**：使用 smart 匹配

```bash
--match-by smart --verbose
```

### 场景 2: 文档已有追踪修订

**解决**：使用 auto 模式（会自动处理）

```bash
--mode auto --verbose
```

如果 auto 模式失败，使用诊断工具：

```bash
python3 ../scripts/analyze_word_structure_deep.py \
  --input "input.docx" \
  --sample-segment "segment-id" \
  --verbose
```

根据诊断结果选择合适的模式。

### 场景 3: 只更新部分翻译

**方案 A**：准备部分新翻译（使用 smart 匹配）

只在新翻译文件中放需要更新的翻译，smart 匹配会自动找到对应的旧翻译。

**方案 B**：使用 segment_id 匹配

准备 JSON 格式，只包含需要更新的 segment_id：

```json
{
  "segment-id-1": "新翻译1",
  "segment-id-5": "新翻译5",
  "segment-id-8": "新翻译8"
}
```

### 场景 4: 对比不同翻译引擎

使用不同的作者名：

```bash
# Gemini 翻译
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "gemini_translations.txt" \
  --output "output_gemini.docx" \
  --author "Gemini"

# Claude 翻译
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "claude_translations.txt" \
  --output "output_claude.docx" \
  --author "Claude"
```

在 Word 中可以按作者筛选修订，方便对比。

---

## 性能优化

### 处理大文档

如果文档很大（> 100 行），考虑：

1. **分批处理**
   - 将翻译分成多个批次
   - 每次处理一部分

2. **使用 segment_id 匹配**（如果可能）
   - 比 smart 匹配更快
   - 适合确定顺序或有 ID 映射的情况

### 减少重复工作

如果需要多次运行，保留中间文件：

```bash
# 第一次运行，保留临时文件
python3 ../scripts/run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_translations.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --keep-temp

# 之后只需重新运行步骤 3
python3 ../scripts/update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "/tmp/fc_insider_*/translations.json" \
  --output "output_v2.docx" \
  --author "Your Name"
```

---

## 避免常见错误

### ❌ 错误 1: 不使用 --verbose

**问题**：遇到错误时难以调试

**解决**：总是使用 `--verbose`

### ❌ 错误 2: 使用 index 匹配

**问题**：顺序稍有不对就全错

**解决**：使用 `smart` 匹配

### ❌ 错误 3: 不检查预览

**问题**：配对错误未发现

**解决**：总是检查变更预览

### ❌ 错误 4: 包含占位符行

**问题**：行数不匹配

**解决**：删除占位符行

### ❌ 错误 5: 不在 Word 中验证

**问题**：问题到最后才发现

**解决**：应用后立即在 Word 中检查

---

## 总结：黄金法则

1. **✅ 使用 smart 匹配** - 顺序无关，自动配对
2. **✅ 总是使用 --verbose** - 查看详细信息
3. **✅ 检查预览** - 确认配对正确
4. **✅ 小批量测试** - 先测试再全量
5. **✅ 在 Word 中验证** - 确认追踪修订正确
6. **✅ 保留版本** - 便于回溯和对比
7. **❌ 不要包含占位符** - 确保行数正确
8. **❌ 避免 index 匹配** - 除非100%确定顺序

遵循这些最佳实践，翻译更新工作将更加高效和可靠！
