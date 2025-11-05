# FC Insider Translator - Claude Skills 环境指南

## ✅ 适用于 Claude Skills 环境

这个版本**专门为 Claude Skills 环境优化**，不依赖任何外部工具，只使用 Python 标准库和 python-docx。

---

## 🎯 与原始方案的对比

### 原始方案（需要外部工具）
```
❌ 需要 Pandoc（外部命令行工具）
❌ 需要 /mnt/skills/public/docx（不存在）
❌ 需要 unpack/pack 流程
```

### Claude Skills 简化方案（推荐）
```
✅ 只需要 python-docx（自动安装）
✅ 纯 Python 实现
✅ 直接操作 DOCX 文件
✅ 自动检查并安装依赖
```

---

## 🚀 快速开始

### 一键运行（推荐）

```bash
bash run_workflow_simple.sh input.docx new_translations.json output.docx
```

就这么简单！脚本会自动：
1. 检查并安装 python-docx
2. 提取表格
3. 生成对照表
4. 应用追踪修订

---

## 📦 文件说明

### Claude Skills 环境专用文件

| 文件 | 用途 | 依赖 |
|------|------|------|
| `extract_table_simple.py` | 提取表格为 Markdown | python-docx |
| `update_fc_insider_simple.py` | 应用追踪修订 | python-docx |
| `run_workflow_simple.sh` | 自动化脚本 | 上述两个脚本 |
| `generate_translation_mapping.py` | 生成对照表 | 无（标准库） |
| `tag_protector.py` | 标签保护 | 无（标准库） |

### 其他文件（供参考）

| 文件 | 说明 | 状态 |
|------|------|------|
| `extract_table_to_markdown.py` | 需要 Pandoc | ⚠️ 需外部工具 |
| `update_fc_insider_v3.py` | 需要 docx skill | ⚠️ 需外部依赖 |
| `run_translation_workflow.sh` | 完整流程（需 unpack/pack） | ⚠️ 需外部工具 |

---

## 📋 详细步骤

### 步骤 1：提取表格

```bash
python3 extract_table_simple.py input.docx table.md
```

**输出**: `table.md` - Markdown 格式的表格

**示例输出**:
```markdown
# FC Insider Translation Table

## Table 1

| Segment ID | Status | Source | Target |
|------------|--------|--------|--------|
| 7bb0408a-1 | Final | Hello world | 你好世界 |
| 7bb0408a-2 | Final | How are you? | 你好吗？ |
```

### 步骤 2：准备新译文

创建 `new_translations.json`:
```json
{
  "7bb0408a-1": "更好的翻译 1",
  "7bb0408a-2": "更好的翻译 2"
}
```

### 步骤 3：生成对照表

```bash
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_translations.json \
  --output translations.json
```

**可选：预览变更**
```bash
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_translations.json \
  --preview-only
```

### 步骤 4：应用追踪修订

```bash
python3 update_fc_insider_simple.py \
  --input input.docx \
  --translations translations.json \
  --output output.docx \
  --author "Your Name"
```

**完成！** 输出文件包含追踪修订标记。

---

## 🔧 依赖管理

### 自动安装（推荐）

运行 `run_workflow_simple.sh` 会自动检查并安装依赖。

### 手动安装

```bash
pip3 install --user python-docx
```

### 验证安装

```bash
python3 -c "from docx import Document; print('✓ python-docx 可用')"
```

---

## 💡 使用场景

### 场景 1：简单翻译更新（最常用）

```bash
# 一键完成
bash run_workflow_simple.sh input.docx new_trans.json output.docx
```

### 场景 2：需要审核对照表

```bash
# 步骤 1-2：提取表格
python3 extract_table_simple.py input.docx table.md

# 步骤 3：生成对照表并预览
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.json \
  --preview-only

# 检查无误后，生成对照表
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.json \
  --output translations.json

# 步骤 4：应用修订
python3 update_fc_insider_simple.py \
  --input input.docx \
  --translations translations.json \
  --output output.docx
```

### 场景 3：AI 生成译文

在 Claude Skills 中：

```python
# 1. 提取表格
!python3 extract_table_simple.py input.docx table.md

# 2. 让 Claude 阅读 table.md 并生成改进的译文
# （Claude 会输出 JSON 格式的新译文）

# 3. 保存 Claude 的输出为 new_trans.json

# 4. 应用翻译
!bash run_workflow_simple.sh input.docx new_trans.json output.docx
```

---

## 🐛 故障排查

### 问题 1：python-docx 未安装

**错误**:
```
ModuleNotFoundError: No module named 'docx'
```

**解决**:
```bash
pip3 install --user python-docx
```

### 问题 2：权限错误

**错误**:
```
Permission denied: ./run_workflow_simple.sh
```

**解决**:
```bash
chmod +x run_workflow_simple.sh
bash run_workflow_simple.sh input.docx new_trans.json
```

### 问题 3：表格提取为空

**原因**: 文档中可能没有表格或表格格式不标准

**调试**:
```bash
python3 -c "
from docx import Document
doc = Document('input.docx')
print(f'表格数量: {len(doc.tables)}')
if doc.tables:
    print(f'第一个表格行数: {len(doc.tables[0].rows)}')
"
```

### 问题 4：segment_id 匹配失败

**解决**: 使用行索引匹配
```bash
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.json \
  --match-by index \
  --output translations.json
```

---

## ⚡ 性能说明

### 处理速度

| 文档大小 | 表格行数 | 预计时间 |
|---------|---------|---------|
| 小型 | < 100 | < 5 秒 |
| 中型 | 100-500 | 5-15 秒 |
| 大型 | 500-1000 | 15-30 秒 |

### 内存使用

- 提取表格：低（< 50MB）
- 应用修订：中等（取决于文档大小）

---

## 📊 与原始方案的技术对比

| 特性 | 原始方案 | Claude Skills 简化方案 |
|------|---------|----------------------|
| 外部依赖 | Pandoc, docx skill | 无（只需 python-docx） |
| 工作流程 | unpack → 修改 → pack | 直接操作 DOCX |
| 安装复杂度 | 高（需系统级安装） | 低（pip install） |
| 可移植性 | 低（依赖环境） | 高（纯 Python） |
| 调试难度 | 高（XML 操作） | 中等（python-docx API） |
| 追踪修订 | ✅ 支持 | ✅ 支持 |
| 标签保护 | ✅ 支持 | ✅ 支持 |

---

## 🎓 工作流程图

### Claude Skills 简化方案

```
input.docx
    ↓
[extract_table_simple.py]
    ↓
table.md (AI 友好格式)
    ↓
[人工/AI 生成新译文]
    ↓
new_translations.json
    ↓
[generate_translation_mapping.py]
    ↓
translations.json (对照表)
    ↓
[update_fc_insider_simple.py]
    ↓
output.docx (含追踪修订)
```

**一键执行**:
```bash
bash run_workflow_simple.sh input.docx new_trans.json output.docx
```

---

## ✅ 验证结果

### 检查追踪修订

在 Word 中打开 `output.docx`：
1. 点击"审阅" → "追踪修订"
2. 应该看到红色删除和蓝色插入标记
3. 可以逐个接受或拒绝修订

### 命令行验证（可选）

```bash
# 提取 XML 检查
python3 -c "
from docx import Document
from docx.oxml.ns import qn

doc = Document('output.docx')
xml = doc._element.xml.decode('utf-8')

del_count = xml.count('<w:del')
ins_count = xml.count('<w:ins')

print(f'删除标记: {del_count}')
print(f'插入标记: {ins_count}')
"
```

---

## 📝 最佳实践

### 1. 始终备份原始文件

```bash
cp input.docx input.docx.backup
```

### 2. 先预览再应用

```bash
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.json \
  --preview-only
```

### 3. 分批处理大型文档

如果文档很大（> 1000 行），考虑分批处理：
```json
{
  "translations": [
    // 第一批：前 500 个
  ]
}
```

### 4. 使用版本控制

```bash
git add translations.json
git commit -m "Add translations batch 1"
```

---

## 🚀 高级用法

### 与 Claude AI 集成

```python
# 在 Claude Skills 中运行

# 1. 提取表格
extract_result = subprocess.run([
    'python3', 'extract_table_simple.py',
    'input.docx', 'table.md'
], capture_output=True)

# 2. 读取表格内容
with open('table.md', 'r') as f:
    table_content = f.read()

# 3. 让 Claude 改进译文
# （Claude 会基于 table_content 生成新译文）

# 4. 应用翻译
subprocess.run([
    'bash', 'run_workflow_simple.sh',
    'input.docx', 'new_trans.json', 'output.docx'
])
```

---

## 📞 获取帮助

### 查看脚本帮助

```bash
python3 extract_table_simple.py --help
python3 generate_translation_mapping.py --help
python3 update_fc_insider_simple.py --help
bash run_workflow_simple.sh --help
```

### 调试模式

添加 `-v` 或 `--verbose` 参数（如果脚本支持）

### 常见问题

1. **表格为空** → 检查 Word 文档是否真的包含表格
2. **匹配失败** → 使用 `--match-by index` 而不是 segment_id
3. **编码错误** → 确保文件以 UTF-8 编码保存

---

## 🎉 总结

Claude Skills 简化方案通过以下方式解决了原始方案的问题：

1. **无外部依赖** - 只需 python-docx（自动安装）
2. **纯 Python** - 易于调试和修改
3. **直接操作 DOCX** - 无需 unpack/pack 流程
4. **自动化** - 一键执行完整流程
5. **兼容性好** - 适用于任何 Python 3.6+ 环境

**立即开始使用**：
```bash
bash run_workflow_simple.sh input.docx new_translations.json output.docx
```

就这么简单！ 🎊
