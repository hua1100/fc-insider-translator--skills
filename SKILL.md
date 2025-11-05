---
name: fc-insider-translator
description: 使用追蹤修訂將翻譯批量更新到 FC Insider DOCX 文件的四欄表格結構中。適用於批量翻譯整理需求，且僅允許部分腳本執行以強化安全性。支持混合方案（Word→Markdown→對照表→XML追蹤修訂）解決AI解析表格錯誤問題。
allowed-tools: "scripts/update_fc_insider_v3.py,scripts/tag_protector,scripts/extract_table_to_markdown.py,scripts/generate_translation_mapping.py,scripts/run_translation_workflow.sh"
---
# fc-insider-translator

## 🚀 Claude Skills 環境快速開始（推薦）

### ⭐ 新版：使用 MarkItDown（最準確）

**使用 Microsoft MarkItDown 提供更準確的表格提取** → 詳見 [MARKITDOWN_GUIDE.md](MARKITDOWN_GUIDE.md)

```bash
bash run_workflow_markitdown.sh input.docx new_translations.json output.docx
```

**特點**：
- ⭐ **使用 MarkItDown**（專為 LLM 優化的文檔轉換）
- ✅ **更準確的表格提取**（解決 Target segment 識別問題）
- ✅ 自動安裝依賴（markitdown + python-docx）
- ✅ 完整追蹤修訂支持

### 備選：標準版本（如果 MarkItDown 不可用）

**適用於 Claude Skills 環境的簡化方案** → 詳見 [CLAUDE_SKILLS_GUIDE.md](CLAUDE_SKILLS_GUIDE.md)

```bash
bash run_workflow_simple.sh input.docx new_translations.json output.docx
```

**特點**：
- ✅ 純 python-docx 實現，無需外部工具
- ✅ 自動檢查並安裝依賴
- ⚠️ 表格提取可能不如 MarkItDown 準確

---

## ⚠️ 其他環境：混合方案（需要 Pandoc）

如果你**不在 Claude Skills 環境**，或需要更高級的功能，可使用混合方案：

→ 詳見 [WORKFLOW.md](WORKFLOW.md)

### 混合方案概述

混合方案將 **讀取** 和 **寫入** 分離，解決 AI 直接解析 Word XML 的問題：

1. **讀取階段**：Word → Markdown（AI 友好格式）
   - 使用 `extract_table_to_markdown.py`（需要 Pandoc 或 docx2python）

2. **分析階段**：基於 Markdown 生成對照表
   - 使用 `generate_translation_mapping.py`

3. **寫入階段**：保持原有 XML + 追蹤修訂
   - 使用 `update_fc_insider_v3.py`（需要 unpack/pack）

**快速開始**：
```bash
# 需要先安裝 Pandoc
bash run_translation_workflow.sh input.docx new_translations.json output.docx
```

---

## 📚 文檔導航

- **[CLAUDE_SKILLS_GUIDE.md](CLAUDE_SKILLS_GUIDE.md)** - Claude Skills 環境專用（推薦）
- **[WORKFLOW.md](WORKFLOW.md)** - 完整混合方案（需要 Pandoc）
- **[README.md](README.md)** - 項目概覽和技術對比
- **[quickstart.md](quickstart.md)** - 原始 XML 方案參考
- **[xml_patterns.md](xml_patterns.md)** - XML 結構參考

---

## 使用規範與安全提醒
- 禁止生成或修改任何 Python 腳本。
- 僅允許調用 scripts/ 資料夾中的以下腳本：
  - `update_fc_insider_v3.py`（XML 追蹤修訂）
  - `tag_protector.py`（標籤保護）
  - `extract_table_to_markdown.py`（表格提取）
  - `generate_translation_mapping.py`（對照表生成）
  - `run_translation_workflow.sh`（自動化工作流程）
- 不得創建替代腳本。
- 若遇到錯誤，應僅輸出錯誤訊息並請求人工檢查，不可嘗試自動重寫腳本。

# FC Insider 翻譯更新 Skill



## 概述

本 Skill 專門處理 FC Insider 格式的 DOCX 文件翻譯更新：
- 四欄表格結構（Segment ID | Status | Source | Target）
- 使用追蹤修訂標記變更
- 高效處理包含 `<51>`, `<52>` 等標籤的文本
- 批量處理以最小化 token 消耗
- 必須使用SKILLS包中的腳本update_fc_insider_v3.py，不得在執行任務中自己生成其他腳本

## 關鍵優化

### 1. 標籤保護策略（解決 `<51>` 衝突）

FC Insider 文件的 Target segment 包含 `<51>`, `<52>` 等標籤，這些是**純文本**，不是 XML 元素。

**問題**：使用 `get_node(contains="<51>")` 會失敗，因為 `<51>` 被當作 XML 標籤解析。

**解決方案**：使用 Unicode 相似字符臨時替換
```python
from scripts.tag_protector import protect_tags, restore_tags

# 在查找前保護
search_text = protect_tags("這是 <51> 測試")  # → "這是 ⟨51⟩ 測試"
# ...

# 替換時也使用保護後的文本
# V3 優化：在 XML 內容中不執行 restore_tags，保留 ⟨⟩ 字符以避免 XML 解析錯誤。
重要：使用 Unicode 字符（⟨ U+27E8, ⟩ U+27E9）而非 HTML 實體，避免二次轉義。


###2. 段落清理/標準化 (V3 核心修正)
在替換前，會執行「段落內容清理」邏輯：

目的： 消除因 Word 編輯歷史導致的 文本碎片化 問題。

機制： 聚合 <w:p> 內所有 Runs 的文本和格式，然後替換整個段落。這確保了替換操作的目標是單一、標準化的 XML 結構。

### 3. 使用 Document 類別（docx skill 最佳實踐）

**不要**自己操作 XML 字串，使用已驗證的 Document 類別方法：

```python
import sys
sys.path.insert(0, '/mnt/skills/public/docx')
from scripts.document import Document

# 初始化（啟用追蹤修訂）
doc = Document(
    'unpacked_doc',
    author="Claude",
    rsid="00AB12CD",        # 從 unpack 獲取
    track_revisions=True
)

# 查找節點
old_node = doc["word/document.xml"].get_node(
    tag="w:r",
    contains=protected_text  # 使用保護後的文本
)

# 保留格式
rpr_tags = old_node.getElementsByTagName("w:rPr")
rpr = rpr_tags[0].toxml() if rpr_tags else ""

# 替換節點（自動添加追蹤修訂）
replacement = f'''
<w:del>
    <w:r>
        {rpr}
        <w:delText>{protected_old_text}</w:delText>
    </w:r>
</w:del>
<w:ins>
    <w:r>
        {rpr}
        <w:t>{protected_new_text}</w:t>
    </w:r>
</w:ins>
'''

doc["word/document.xml"].replace_node(old_node, replacement)

# 保存
doc.save()
```

### 3. 智能查找策略（減少 token）

不要盲目查找，使用**上下文線索**縮小範圍：

```python
# ❌ 低效：直接查找文本（可能有多個匹配）
node = doc["word/document.xml"].get_node(tag="w:r", contains="測試")

# ✅ 高效：先定位 segment_id，再在該區域查找
# 1. 找到包含 segment_id 的表格行
row_node = doc["word/document.xml"].get_node(tag="w:tr", contains=segment_id)

# 2. 在該行內查找第 4 個 <w:tc>（使用 minidom 遍歷）
cells = row_node.getElementsByTagName("w:tc")
target_cell = cells[3] if len(cells) >= 4 else None

# 3. 在 target_cell 內查找文本（範圍大幅縮小）
```

## 使用流程

### 步驟 1: 準備翻譯數據

翻譯數據應為 JSON 格式：

```json
{
  "translations": [
    {
      "segment_id": "7bb0408a-1",
      "old_text": "舊的翻譯",
      "new_text": "新的翻譯"
    }
  ]
}
```

### 步驟 2: 解包 DOCX

```bash
python /mnt/skills/public/docx/ooxml/scripts/unpack.py input.docx unpacked/
```

**重要**：記錄 unpack 腳本輸出的 **RSID**，例如：
```
Suggested RSID for new content: 00AB12CD
```

### 步驟 3: 執行批量更新

```bash
python scripts/update_fc_insider_v3.py \
  --unpacked unpacked/ \
  --translations translations.json \
  --rsid 00AB12CD \
  --author "Claude"
```

### 步驟 4: 打包 DOCX

```bash
python /mnt/skills/public/docx/ooxml/scripts/pack.py \
  unpacked/ \
  output_with_tracking.docx
```

## 腳本詳解

### scripts/tag_protector.py

保護和恢復標籤的工具函數：

```python
def protect_tags(text):
    """將 <51> 等標籤替換為安全字符（⟨51⟩）"""
    return text.replace('<', '⟨').replace('>', '⟩')

def restore_tags(text):
    """恢復原始標籤"""
    return text.replace('⟨', '<').replace('⟩', '>')
```

**為什麼需要這個？**
- `get_node(contains="<51>")` 會失敗（XML 解析錯誤）
- `get_node(contains="⟨51⟩")` 可以正常工作
- 最後統一恢復標籤

### scripts/update_fc_insider_v3.py

請見scripts/update_fc_insider_v3.py



## 常見問題



### Q: 如何處理 `<51>` 標籤？

A: 使用 Unicode 相似字符臨時保護：
```python
# 查找前保護
search_text = protect_tags("文字 <51>")  # → "文字 ⟨51⟩"

# 使用保護後的文本
node = doc["word/document.xml"].get_node(contains=search_text)

# 全部完成後統一恢復
xml_content = restore_tags(xml_content)
```



### Q: 如何驗證追蹤修訂？

A: 檢查生成的標記數量：
```bash
grep -c '<w:del>' unpacked/word/document.xml
grep -c '<w:ins>' unpacked/word/document.xml
```

應該各有 N 個（N = 更新的 segment 數量）

## 錯誤處理協定

若腳本執行發生錯誤：
1. 僅回報錯誤訊息與 stack trace；
2. 不可自動生成或修改任何腳本；
3. 不可使用 minidom、BeautifulSoup 等替代解析方案；
4. 若需要修正，應請求人工提供更新版；
5. 不可臆測腳本內容。

## 限制

- 假設文件結構為四欄表格
- Segment ID 必須在第 1 欄
- Target segment 必須在第 4 欄
- 不支持嵌套表格

## 進階使用

### 詳細的 XML 結構參考

查看 [references/xml_patterns.md](references/xml_patterns.md) 了解：
- FC Insider 表格的完整 XML 結構
- 如何識別和跳過 Tag 樣式
- 追蹤修訂的 XML 模式
- 標籤保護的技術細節

### 快速開始範例

查看 [references/quickstart.md](references/quickstart.md) 了解：
- 完整的端到端範例
- 自動化腳本
- 常見錯誤排查
- 驗證方法

## 相關文檔

- [docx skill 文檔](../../public/docx/SKILL.md) - Document 類別完整參考
- [OOXML 追蹤修訂指南](../../public/docx/ooxml.md) - 追蹤修訂的技術細節
