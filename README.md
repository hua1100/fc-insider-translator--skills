# FC Insider Translator - 混合方案升級

## 🎯 解決的問題

### 原始問題
在使用 AI 直接解析 Word 表格的 XML 結構時，經常遇到：
- ❌ **判斷表格為空** - 即使表格有內容
- ❌ **無法正確定位單元格** - XML 結構複雜
- ❌ **解析錯誤** - `<51>`, `<52>` 等標籤衝突
- ❌ **調試困難** - XML 不易閱讀

### 解決方案：混合方案

將 **讀取（Word → Markdown）** 和 **寫入（XML + 追蹤修訂）** 分離：

```
Word DOCX
  ↓
├─→ [讀取] → Markdown（AI 友好）→ 生成對照表
│                                    ↓
└─→ [寫入] ← XML 追蹤修訂 ←────────────┘
  ↓
Word DOCX + Track Changes
```

---

## 🚀 快速開始

### 一鍵運行

```bash
bash run_translation_workflow.sh input.docx new_translations.json output.docx
```

### 分步執行

#### 步驟 1：提取表格為 Markdown
```bash
python extract_table_to_markdown.py input.docx table.md
```

#### 步驟 2：準備新譯文
創建 `new_translations.json`：
```json
{
  "7bb0408a-1": "新的翻譯 1",
  "7bb0408a-2": "新的翻譯 2"
}
```

#### 步驟 3：生成對照表
```bash
python generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_translations.json \
  --output translations.json
```

#### 步驟 4：解包 Word
```bash
python /mnt/skills/public/docx/ooxml/scripts/unpack.py input.docx unpacked/
# 記錄輸出的 RSID
```

#### 步驟 5：應用追蹤修訂
```bash
python update_fc_insider_v3.py \
  --unpacked unpacked/ \
  --translations translations.json \
  --rsid 00AB12CD \
  --author "Your Name"
```

#### 步驟 6：打包 Word
```bash
python /mnt/skills/public/docx/ooxml/scripts/pack.py unpacked/ output.docx
```

---

## 📦 新增文件

### 核心腳本

| 文件 | 功能 | 用途 |
|------|------|------|
| `extract_table_to_markdown.py` | Word → Markdown | 提取表格為 AI 友好格式 |
| `generate_translation_mapping.py` | 生成對照表 | 匹配新舊譯文 |
| `run_translation_workflow.sh` | 自動化流程 | 一鍵執行完整流程 |

### 文檔

| 文件 | 內容 |
|------|------|
| `WORKFLOW.md` | 完整工作流程說明 |
| `README.md` | 本文檔 |
| `SKILL.md` | Skill 完整文檔（已更新） |

### 保留的原始文件

| 文件 | 狀態 |
|------|------|
| `update_fc_insider_v3.py` | ✅ 保留（寫入階段仍使用） |
| `tag_protector.py` | ✅ 保留（標籤保護仍需要） |
| `track_changes.py` | ⚠️ 保留（供參考） |

---

## 🔧 依賴安裝

### 必需（推薦）
```bash
# Pandoc（用於 Word → Markdown）
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc
```

### 可選
```bash
# docx2python（替代 Pandoc，提供更精細控制）
pip install docx2python
```

---

## 💡 使用場景

### 場景 1：簡單翻譯更新
```bash
# 一鍵完成
bash run_translation_workflow.sh input.docx new_trans.json output.docx
```

### 場景 2：需要預覽變更
```bash
# 步驟 1-3：生成對照表
python extract_table_to_markdown.py input.docx table.md
python generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.json \
  --preview-only  # 只預覽，不保存

# 檢查無誤後，去掉 --preview-only 再次運行
```

### 場景 3：AI 生成譯文
```bash
# 1. 提取表格
python extract_table_to_markdown.py input.docx table.md

# 2. 讓 AI 基於 table.md 生成新譯文
# （手動或通過 AI API）

# 3. 將 AI 輸出轉換為 JSON 格式
# {
#   "segment_id": "new_translation",
#   ...
# }

# 4. 繼續後續步驟
```

---

## 🎨 工作流程對比

### 原始方案（直接 XML）
```
優點:
  ✅ 一步到位
  ✅ 不需要額外工具

缺點:
  ❌ AI 容易誤判表格結構
  ❌ XML 解析錯誤頻繁
  ❌ 調試困難
```

### 混合方案（推薦）
```
優點:
  ✅ AI 準確理解表格（Markdown 清晰）
  ✅ 可預覽和驗證變更
  ✅ 易於調試
  ✅ 分離關注點（讀寫分離）
  ✅ 保持追蹤修訂的精確性

缺點:
  ⚠️ 需要多個步驟（可用腳本自動化）
  ⚠️ 需要安裝 Pandoc
```

---

## 🔍 故障排查

### 問題 1：Pandoc 未安裝
```
錯誤: ✗ 錯誤：未找到 Pandoc
```

**解決**：
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc
```

### 問題 2：表格提取不正確
```bash
# 嘗試使用 docx2python
pip install docx2python
python extract_table_to_markdown.py input.docx table.md --method docx2python
```

### 問題 3：segment_id 匹配失敗
```bash
# 使用行索引匹配
python generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.txt \
  --match-by index
```

### 問題 4：追蹤修訂未生效
```bash
# 檢查 XML 中的追蹤修訂標記
grep -c '<w:del>' unpacked/word/document.xml
grep -c '<w:ins>' unpacked/word/document.xml

# 應該有 N 個（N = 變更數量）
```

---

## 📊 技術架構

### 讀取階段（Word → Markdown）
- **工具**：Pandoc 或 docx2python
- **輸出**：Markdown 表格
- **優勢**：AI 友好、易讀、不會誤判

### 分析階段（生成對照表）
- **輸入**：Markdown 表格 + 新譯文
- **輸出**：`translations.json`
- **功能**：匹配、驗證、預覽

### 寫入階段（XML + 追蹤修訂）
- **方法**：保持原有 `update_fc_insider_v3.py`
- **優勢**：成熟、精確、保留格式

---

## 📚 文檔索引

1. **[README.md](README.md)**（本文檔）- 快速開始
2. **[WORKFLOW.md](WORKFLOW.md)** - 詳細工作流程
3. **[SKILL.md](SKILL.md)** - 完整 Skill 文檔
4. **[quickstart.md](quickstart.md)** - 快速範例（原始方案）
5. **[xml_patterns.md](xml_patterns.md)** - XML 結構參考

---

## 🤝 貢獻

如果你有改進建議或發現問題，請：
1. 記錄詳細的錯誤信息
2. 提供示例文件（如果可以）
3. 說明你的使用場景

---

## 📝 更新日誌

### v2.0（混合方案）
- ✨ 新增 Word → Markdown 提取功能
- ✨ 新增翻譯對照表生成器
- ✨ 新增自動化工作流程腳本
- ✨ 支持 Pandoc 和 docx2python 兩種提取方法
- ✨ 新增變更預覽和驗證功能
- 📚 完善文檔（WORKFLOW.md、README.md）
- 🔧 更新 SKILL.md 和 allowed-tools

### v1.0（原始 XML 方案）
- 基礎 XML 追蹤修訂功能
- 標籤保護機制
- 四欄表格支持

---

## 🎓 學習資源

### 理解工作流程
1. 先閱讀 [README.md](README.md)（本文檔）了解概念
2. 查看 [WORKFLOW.md](WORKFLOW.md) 了解詳細步驟
3. 運行 `run_translation_workflow.sh` 體驗完整流程

### 深入技術細節
1. [SKILL.md](SKILL.md) - XML 處理和追蹤修訂
2. [xml_patterns.md](xml_patterns.md) - Word XML 結構
3. 源碼註釋 - 各個 Python 腳本

---

## ⚡ 性能提示

### 優化建議
1. **使用 Pandoc**（更快）：適合大多數場景
2. **使用 docx2python**（更精確）：需要過濾特定樣式時
3. **批量處理**：一次處理多個文檔時，考慮並行化

### 資源消耗
- Pandoc：低（秒級轉換）
- docx2python：中等（適合中等大小文檔）
- XML 處理：取決於表格大小

---

## 📄 授權

本 Skill 為內部工具，遵循項目整體授權。

---

## 📧 聯繫

如有問題或建議，請通過項目渠道聯繫維護者。

---

**現在就開始使用混合方案，告別 AI 解析 Word 表格的困擾！** 🎉
