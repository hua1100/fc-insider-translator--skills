# 从旧版本迁移

从 v1.0 迁移到 v2.0 的完整指南。

---

## 版本对比

### v1.0（旧版本）

**特点**：
- 基础的表格提取
- 简单的索引匹配
- 手动三步流程
- 需要确保顺序一致

**局限**：
- ❌ 顺序依赖
- ❌ 无法处理追踪修订
- ❌ 占位符行会被错误匹配
- ❌ 需要手动执行多个步骤

### v2.0（当前版本）

**新特性**：
- ✅ 智能匹配功能（顺序无关）
- ✅ 追踪修订自动处理
- ✅ 占位符自动过滤
- ✅ 一键执行脚本
- ✅ 深度诊断工具
- ✅ 详细的 verbose 输出

**优势**：
- 更智能
- 更可靠
- 更简单
- 更容易调试

---

## 迁移步骤

### 步骤 1: 确认环境

确保已安装必需的依赖：

```bash
pip install markitdown python-docx lxml
```

### 步骤 2: 了解新的脚本对应关系

| v1.0 | v2.0 | 说明 |
|------|------|------|
| `run_workflow_markitdown.sh` | `run_complete_workflow.py` | 一键执行脚本 |
| `run_workflow_simple.sh` | `run_complete_workflow.py` | 一键执行脚本 |
| `extract_table_markitdown.py` | `extract_table_markitdown_simple.py` | 表格提取 |
| `generate_translation_mapping.py` | `generate_translation_mapping.py` | 映射生成（增强版） |
| `update_fc_insider.py` | `update_fc_insider_tracked.py` | 应用翻译（增强版） |
| - | `analyze_word_structure_deep.py` | 新增：诊断工具 |

### 步骤 3: 更新命令

#### 旧版命令（v1.0）

```bash
# 旧版：三步流程
python3 extract_table_markitdown.py \
  --input "input.docx" \
  --output "table.md"

python3 generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json"

python3 update_fc_insider.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx"
```

#### 新版命令（v2.0）

**方式 1: 一键执行（推荐）**

```bash
# 新版：一键完成
python3 run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_trans.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

**方式 2: 分步执行（高级用户）**

```bash
# 步骤 1: 提取表格
python3 extract_table_markitdown_simple.py \
  --input "input.docx" \
  --output "table.md"

# 步骤 2: 生成映射（智能匹配）
python3 generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json" \
  --match-by smart \  # 新增参数！
  --verbose             # 新增参数！

# 步骤 3: 应用翻译
python3 update_fc_insider_tracked.py \  # 新脚本名！
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "Your Name" \  # 新增参数！
  --mode auto \            # 新增参数！
  --verbose                # 新增参数！
```

---

## 新参数说明

### generate_translation_mapping.py

#### 新增：--match-by

**用途**：选择匹配方式

**可选值**：
- `smart` - 智能匹配（推荐，顺序无关）⭐
- `segment_id` - 通过 ID 匹配（默认，需要 JSON）
- `index` - 按索引匹配（旧方式，顺序依赖）

**示例**：
```bash
--match-by smart  # 推荐！
```

#### 新增：--skip-placeholder-filter

**用途**：跳过占位符过滤（默认启用）

**通常不需要使用**，除非你想保留占位符行。

#### 增强：--verbose

**用途**：显示详细信息

**新增输出**：
- 占位符过滤详情
- 智能匹配相似度
- 配对示例
- 低相似度警告

**强烈推荐使用**！

### update_fc_insider_tracked.py

#### 新增：--mode

**用途**：选择读取模式

**可选值**：
- `auto` - 自动检测（推荐）⭐
- `read_deleted` - 从删除的文本读取
- `read_inserted` - 从插入的文本读取

**示例**：
```bash
--mode auto  # 推荐！
```

#### 新增：--author

**用途**：设置追踪修订作者名称

**示例**：
```bash
--author "Gemini"
--author "Claude"
```

**推荐**：使用有意义的名称，便于在 Word 中区分。

#### 增强：--verbose

**用途**：显示详细信息

**新增输出**：
- 自动检测结果
- 每行处理状态
- 文本匹配详情

**强烈推荐使用**！

---

## 迁移场景

### 场景 1: 使用 run_workflow_markitdown.sh

**旧版**：
```bash
./run_workflow_markitdown.sh \
  "input.docx" \
  "new_trans.txt" \
  "output.docx"
```

**新版**：
```bash
python3 run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_trans.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

### 场景 2: 手动三步流程

**旧版**：
```bash
# 步骤 1
python3 extract_table_markitdown.py --input "input.docx" --output "table.md"

# 步骤 2
python3 generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json"

# 步骤 3
python3 update_fc_insider.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx"
```

**新版（一键）**：
```bash
python3 run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_trans.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

**新版（分步，如果需要）**：
```bash
# 步骤 1
python3 extract_table_markitdown_simple.py \
  --input "input.docx" \
  --output "table.md"

# 步骤 2（智能匹配）
python3 generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json" \
  --match-by smart \
  --verbose

# 步骤 3（追踪修订处理）
python3 update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "Your Name" \
  --mode auto \
  --verbose
```

### 场景 3: 处理已有追踪修订的文档

**旧版**：
```
❌ 无法处理，会报错
```

**新版**：
```bash
# 自动检测并处理
python3 run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_trans.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --update-mode auto \  # 关键！
  --verbose
```

或使用分步执行：
```bash
# 步骤 3 使用 update_fc_insider_tracked.py
python3 update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "translations.json" \
  --output "output.docx" \
  --author "Your Name" \
  --mode auto \
  --verbose
```

### 场景 4: 新翻译顺序与表格不一致

**旧版**：
```
❌ 顺序必须一致，否则配对错误
```

**新版**：
```bash
# 使用智能匹配
python3 run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_trans.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --match-by smart \  # 关键！
  --verbose
```

---

## 兼容性说明

### 向后兼容

v2.0 **完全兼容** v1.0 的使用方式：

```bash
# v1.0 风格的命令在 v2.0 中仍然有效
python3 generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json"
# ↓ 等同于
python3 generate_translation_mapping.py \
  --markdown "table.md" \
  --new-translations "new_trans.txt" \
  --output "translations.json" \
  --match-by segment_id  # 默认值
```

### 文件格式

v1.0 和 v2.0 使用相同的文件格式：

- 输入：`.docx` 格式的 Word 文档
- 新翻译：纯文本或 JSON
- 映射表：JSON 格式
- 输出：`.docx` 格式的 Word 文档

---

## 常见问题

### Q: 我需要重新准备新翻译文件吗？

**A**: 不需要！v2.0 完全兼容 v1.0 的纯文本格式。

如果你的新翻译顺序与表格不一致，使用 `--match-by smart` 即可。

### Q: 旧的脚本还能用吗？

**A**: 可以，但建议迁移到新版：

- `update_fc_insider.py` → `update_fc_insider_tracked.py`（功能更强大）
- 手动三步 → `run_complete_workflow.py`（一键完成）

### Q: 我之前保存的 translations.json 还能用吗？

**A**: 可以！格式完全相同。

```bash
# 直接使用旧的 translations.json
python3 update_fc_insider_tracked.py \
  --input "input.docx" \
  --translations "old_translations.json" \  # 旧文件
  --output "output.docx" \
  --author "Your Name"
```

### Q: 需要重新学习吗？

**A**: 基本流程不变，只是增加了新功能：

- **一键执行** - 更简单
- **智能匹配** - 更可靠
- **追踪修订处理** - 处理更多场景

建议：
1. 先尝试一键执行（`run_complete_workflow.py`）
2. 如果需要更多控制，使用分步执行
3. 遇到问题使用诊断工具

### Q: v2.0 的性能如何？

**A**: 性能略有提升：

- 智能匹配：对于小文档（< 50 行）几乎无感，对于大文档（> 100 行）可能多花 1-2 秒
- 占位符过滤：几乎无性能影响
- 追踪修订处理：与 v1.0 相当

总体：性能差异可忽略，功能提升显著。

---

## 推荐迁移路径

### 阶段 1: 尝试一键执行（5 分钟）

```bash
python3 run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_trans.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --verbose
```

体验最简单的使用方式。

### 阶段 2: 启用智能匹配（10 分钟）

```bash
python3 run_complete_workflow.py \
  --input "input.docx" \
  --new-translations "new_trans.txt" \
  --output "output.docx" \
  --author "Your Name" \
  --match-by smart \  # 新增
  --verbose
```

查看智能匹配的效果和相似度分数。

### 阶段 3: 处理复杂场景（按需）

- 如果文档有追踪修订：使用 `--mode auto`
- 如果顺序不一致：使用 `--match-by smart`
- 如果遇到问题：使用诊断工具

### 阶段 4: 完全迁移（1 小时）

1. 更新所有脚本和命令
2. 删除旧的 shell 脚本（如 `run_workflow_markitdown.sh`）
3. 使用新的最佳实践

---

## 获取帮助

### 查看完整文档

- **[SKILL.md](SKILL.md)** - 快速开始
- **[PARAMETERS.md](PARAMETERS.md)** - 参数说明
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排查
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - 最佳实践
- **[ADVANCED.md](ADVANCED.md)** - 高级功能

### 遇到迁移问题？

1. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. 使用 `--verbose` 查看详细输出
3. 使用诊断工具分析问题

---

## 总结

迁移到 v2.0 非常简单：

1. ✅ **向后兼容** - 旧命令仍然有效
2. ✅ **文件格式不变** - 不需要重新准备文件
3. ✅ **一键执行** - 更简单的使用方式
4. ✅ **智能匹配** - 处理顺序不一致
5. ✅ **追踪修订处理** - 处理更多场景

**推荐**：直接使用 `run_complete_workflow.py`，享受 v2.0 的所有新特性！
