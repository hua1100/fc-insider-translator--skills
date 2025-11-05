# MarkItDown 使用指南

## 為什麼使用 MarkItDown？

### 問題

使用 `python-docx` 直接提取表格時，可能遇到：
- ❌ 無法正確提取 Target segment 的內容
- ❌ 複雜表格結構解析錯誤
- ❌ 格式化文本丟失

### 解決方案：MarkItDown

✅ **Microsoft MarkItDown** 是專為 LLM 優化的文檔轉換工具：
- ✅ 更準確的表格提取
- ✅ 保留文檔結構
- ✅ 支持復雜表格
- ✅ 專門設計用於 AI 處理

---

## 🚀 快速開始

### 一鍵運行

```bash
bash run_workflow_markitdown.sh input.docx new_translations.json output.docx
```

腳本會自動：
1. ✅ 安裝 markitdown 和 python-docx
2. ✅ 使用 MarkItDown 提取表格
3. ✅ 生成翻譯對照表
4. ✅ 應用追蹤修訂

---

## 📋 分步執行

### 步驟 1：提取表格（使用 MarkItDown）

```bash
python3 extract_table_markitdown.py input.docx table.md
```

**輸出**：
- `table.md` - Markdown 格式的表格
- 更準確的 Target segment 內容提取

**查看效果**：
```bash
cat table.md

# 檢查 Target segment 是否正確提取
grep "Target" table.md | head -5
```

### 步驟 2：準備新譯文

創建 `new_translations.json`：
```json
{
  "7bb0408a-1": "新的翻譯 1",
  "7bb0408a-2": "新的翻譯 2"
}
```

### 步驟 3：生成對照表

```bash
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_translations.json \
  --output translations.json
```

**預覽變更**：
```bash
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_translations.json \
  --preview-only
```

### 步驟 4：應用追蹤修訂

```bash
python3 update_fc_insider_simple.py \
  --input input.docx \
  --translations translations.json \
  --output output.docx \
  --author "Your Name"
```

---

## 🔧 安裝和配置

### 自動安裝（推薦）

運行工作流程腳本會自動安裝：
```bash
bash run_workflow_markitdown.sh input.docx new_trans.json output.docx
```

### 手動安裝

```bash
# 安裝 markitdown
pip3 install --user markitdown

# 安裝 python-docx
pip3 install --user python-docx
```

### 驗證安裝

```bash
python3 -c "
from markitdown import MarkItDown
print('✓ MarkItDown 可用')

from docx import Document
print('✓ python-docx 可用')
"
```

---

## 📊 效果對比

### 使用 python-docx（舊版）

```bash
python3 extract_table_simple.py input.docx table.md
```

**問題**：
- ❌ Target segment 可能無法正確提取
- ❌ 複雜表格結構可能解析錯誤
- ❌ 某些格式化內容丟失

### 使用 MarkItDown（新版）

```bash
python3 extract_table_markitdown.py input.docx table.md
```

**優勢**：
- ✅ Target segment 準確提取
- ✅ 更好地處理複雜表格
- ✅ 保留重要文檔結構
- ✅ 專為 LLM 優化

---

## 🎯 使用場景

### 場景 1：Target segment 提取失敗

**問題**：
```bash
python3 extract_table_simple.py input.docx table.md
# 結果：Target 列為空或不完整
```

**解決**：
```bash
python3 extract_table_markitdown.py input.docx table.md
# 結果：Target 列正確提取
```

### 場景 2：複雜表格結構

**適用於**：
- 合併單元格
- 嵌套表格
- 多行文本
- 特殊格式

**使用 MarkItDown**：
```bash
bash run_workflow_markitdown.sh complex_table.docx new_trans.json output.docx
```

### 場景 3：批量處理

```bash
# 處理多個文檔
for file in *.docx; do
    output="${file%.docx}_translated.docx"
    bash run_workflow_markitdown.sh "$file" new_translations.json "$output"
done
```

---

## 🔍 故障排查

### 問題 1：markitdown 未安裝

**錯誤**：
```
ModuleNotFoundError: No module named 'markitdown'
```

**解決**：
```bash
pip3 install --user markitdown
```

### 問題 2：提取的表格仍然不正確

**調試**：
```bash
# 查看原始 Markdown 輸出
python3 extract_table_markitdown.py input.docx output.md
cat output.md

# 檢查表格結構
grep "^\|" output.md | head -20
```

**如果問題仍存在**：
1. 檢查 Word 文檔是否有異常格式
2. 嘗試在 Word 中重新保存文檔
3. 確保表格是標準的 Word 表格（不是文本框）

### 問題 3：依賴安裝失敗

**解決**：
```bash
# 升級 pip
python3 -m pip install --upgrade pip

# 重新安裝
pip3 install --user --force-reinstall markitdown python-docx
```

### 問題 4：性能問題（大文檔）

**優化**：
```bash
# MarkItDown 對大文檔的處理可能較慢
# 建議：先測試小文檔，確認效果後再處理大文檔

# 監控進度
python3 extract_table_markitdown.py large_doc.docx output.md --verbose
```

---

## 📈 性能比較

| 方案 | 準確度 | 速度 | 內存 | 依賴 |
|------|--------|------|------|------|
| python-docx | 中等 | 快 | 低 | python-docx |
| MarkItDown | **高** | 中等 | 中等 | markitdown + python-docx |

**推薦**：
- 小型文檔（< 100 行）：兩者都可以
- 中型文檔（100-500 行）：推薦 MarkItDown
- 大型文檔（> 500 行）：推薦 MarkItDown
- 複雜表格：**必須使用 MarkItDown**

---

## 🎓 高級用法

### Python API 直接使用

```python
from markitdown import MarkItDown

# 初始化
md = MarkItDown()

# 轉換本地文件
result = md.convert('document.docx')
markdown_content = result.text_content

# 保存
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)
```

### 處理 URL

```python
from markitdown import MarkItDown

md = MarkItDown()

# 從 URL 轉換
result = md.convert_url('https://example.com/document.docx')
print(result.text_content)
```

### 自定義提取邏輯

```python
from markitdown import MarkItDown
import re

md = MarkItDown()
result = md.convert('input.docx')

# 使用正則表達式提取特定內容
tables = re.findall(r'\|.*\|', result.text_content)
print(f"找到 {len(tables)} 行表格數據")
```

---

## 💡 最佳實踐

### 1. 始終驗證提取結果

```bash
python3 extract_table_markitdown.py input.docx output.md
head -30 output.md  # 檢查前 30 行
```

### 2. 使用預覽模式

```bash
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.json \
  --preview-only
```

### 3. 保留中間文件（調試用）

```bash
# 不使用 --output-json 時，手動保存 Markdown
python3 extract_table_markitdown.py input.docx table.md

# 查看中間結果
cat table.md | less
```

### 4. 批量處理時添加錯誤處理

```bash
for file in *.docx; do
    echo "處理: $file"
    bash run_workflow_markitdown.sh "$file" new_trans.json "output_$file" || {
        echo "錯誤: $file 處理失敗"
        continue
    }
done
```

---

## 🔗 相關資源

### 官方文檔
- [MarkItDown GitHub](https://github.com/microsoft/markitdown)
- [MCP 配置指南](MCP_SETUP.md)

### 本項目文檔
- [CLAUDE_SKILLS_GUIDE.md](CLAUDE_SKILLS_GUIDE.md) - Claude Skills 環境指南
- [WORKFLOW.md](WORKFLOW.md) - 完整工作流程
- [README.md](README.md) - 項目概覽

---

## 🎊 總結

### MarkItDown 優勢

1. **更準確**：專為 LLM 優化，表格提取更準確
2. **易於使用**：Python API 簡單直觀
3. **維護良好**：Microsoft 官方維護
4. **功能豐富**：支持多種文檔格式

### 推薦使用場景

✅ **推薦使用 MarkItDown**：
- Target segment 提取失敗
- 複雜表格結構
- 需要高準確度
- LLM 處理文檔

⚠️ **可使用 python-docx**：
- 簡單表格
- 性能要求高
- 依賴限制

---

## 🚀 立即開始

```bash
# 一鍵運行（推薦）
bash run_workflow_markitdown.sh input.docx new_translations.json output.docx
```

**就這麼簡單！** 🎉
