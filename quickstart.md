# FC Insider 翻譯更新快速開始

## 完整範例

假設您有：
- 原始 DOCX 文件：`FCInsider_Issue6.docx`
- 翻譯結果：`translations.json`

### 1. 準備翻譯 JSON

```json
{
  "translations": [
    {
      "segment_id": "7bb0408a-1",
      "old_text": "這是舊的翻譯",
      "new_text": "這是新的改進翻譯"
    },
    {
      "segment_id": "7bb0408a-2",
      "old_text": "另一段舊翻譯 <51>",
      "new_text": "另一段新翻譯 <51>"
    }
  ]
}
```
※ 特殊標籤 <51>, <52> 會自動保護，請直接使用原文即可

### 2. 解包 DOCX

```bash
python /mnt/skills/public/docx/ooxml/scripts/unpack.py \
  FCInsider_Issue6.docx \
  unpacked/
```

**記錄輸出中的 RSID**，例如：
```
Unpacking DOCX file: FCInsider_Issue6.docx
...
Suggested RSID for new content: 00F91A42
```

### 3. 執行更新

```bash
python scripts/update_with_document.py \
  --unpacked unpacked/ \
  --translations translations.json \
  --rsid 00F91A42 \
  --author "Claude"
```

### 4. 打包 DOCX

```bash
python /mnt/skills/public/docx/ooxml/scripts/pack.py \
  unpacked/ \
  FCInsider_Issue6_Updated.docx
```

### 5. 驗證

```bash
# 檢查追蹤修訂數量
grep -c '<w:del>' unpacked/word/document.xml
grep -c '<w:ins>' unpacked/word/document.xml

# 應該各有 2 個（與翻譯數量相同）
```

## 完整的自動化腳本

```bash
#!/bin/bash
# update_fc_insider.sh

INPUT_DOCX="$1"
TRANSLATIONS_JSON="$2"
OUTPUT_DOCX="${INPUT_DOCX%.docx}_Updated.docx"

# 檢查參數
if [ -z "$INPUT_DOCX" ] || [ -z "$TRANSLATIONS_JSON" ]; then
    echo "用法: $0 <input.docx> <translations.json>"
    exit 1
fi

# 1. 解包
echo "解包 DOCX..."
python /mnt/skills/public/docx/ooxml/scripts/unpack.py \
  "$INPUT_DOCX" \
  unpacked/ \
  > unpack.log 2>&1

# 提取 RSID
if [ -z "$RSID" ]; then
    echo "❌ 無法提取 RSID，請檢查 unpack.log"
    exit 1
fi


# 2. 更新
echo "執行翻譯更新..."
python scripts/update_fc_insider_v3.py\
  --unpacked unpacked/ \
  --translations "$TRANSLATIONS_JSON" \
  --rsid "$RSID" \
  --author "Claude"

# 3. 打包
echo "打包 DOCX..."
python /mnt/skills/public/docx/ooxml/scripts/pack.py \
  unpacked/ \
  "$OUTPUT_DOCX"

# 4. 驗證
echo ""
echo "驗證結果..."
DEL_COUNT=$(grep -c '<w:del>' unpacked/word/document.xml)
INS_COUNT=$(grep -c '<w:ins>' unpacked/word/document.xml)

echo "刪除標記: $DEL_COUNT"
echo "插入標記: $INS_COUNT"
echo "輸出文件: $OUTPUT_DOCX"
echo ""
echo "✓ 完成"
```

使用方式：

```bash
chmod +x update_fc_insider.sh
./update_fc_insider.sh FCInsider_Issue6.docx translations.json
```

## 常見錯誤排查

### 錯誤 1: 找不到 segment

```
ValueError: 找不到 segment: 7bb0408a-1
```

**原因**：Segment ID 不匹配

**解決**：檢查 JSON 中的 segment_id 是否與文檔一致

```bash
# 列出文檔中的前 10 個 segment ID
python -c "
from xml.dom import minidom
dom = minidom.parse('unpacked/word/document.xml')
tables = dom.getElementsByTagName('w:tbl')
for table in tables:
    rows = table.getElementsByTagName('w:tr')
    for i, row in enumerate(rows[:10]):
        cells = row.getElementsByTagName('w:tc')
        if len(cells) >= 1:
            texts = cells[0].getElementsByTagName('w:t')
            if texts and texts[0].firstChild:
                print(f'{i}: {texts[0].firstChild.nodeValue}')
"
```

### 錯誤 2: 找不到文本

```
ValueError: 找不到文本 '舊翻譯' 在 segment: 7bb0408a-1
```

**原因**：old_text 與文檔中的實際文本不符

**解決**：確認 old_text 完全匹配（包括空白、標籤）

```bash
# 查看特定 segment 的 Target cell 內容
python -c "
from xml.dom import minidom

dom = minidom.parse('unpacked/word/document.xml')
segment_id = '7bb0408a-1'

# 找到包含 segment_id 的行
for tr in dom.getElementsByTagName('w:tr'):
    cells = tr.getElementsByTagName('w:tc')
    if len(cells) >= 4:
        # 檢查第 1 欄
        first_cell_texts = cells[0].getElementsByTagName('w:t')
        if first_cell_texts and first_cell_texts[0].firstChild:
            if first_cell_texts[0].firstChild.nodeValue == segment_id:
                # 輸出第 4 欄的所有文本
                target_texts = cells[3].getElementsByTagName('w:t')
                print('Target cell 內容:')
                for t in target_texts:
                    if t.firstChild:
                        print(repr(t.firstChild.nodeValue))
"
```

### 錯誤 3: XML 解析錯誤

```
xml.parsers.expat.ExpatError: not well-formed
```

**原因**：翻譯中包含特殊 XML 字符未處理

**解決**：檢查是否使用了 `protect_tags()`

腳本應該自動處理，如果仍有問題，手動檢查：

```python
from scripts.tag_protector import protect_tags, restore_tags

# 測試保護
text = "測試 <51> 文字"
protected = protect_tags(text)
print(f"原文: {text}")
print(f"保護: {protected}")
print(f"是否改變: {text != protected}")
```
