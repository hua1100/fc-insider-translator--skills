

# FC Insider XML 結構參考

## 表格結構

FC Insider 使用**四欄表格**：

```
| 第 1 欄          | 第 2 欄         | 第 3 欄        | 第 4 欄        |
|-----------------|----------------|---------------|---------------|
| Segment ID      | Segment status | Source (英文)  | Target (中文)  |
```

> ⚠️ 第 4 欄是翻譯目標（Target），我們主要更新這一欄。

---

## XML 結構範例

### 完整的表格行

```xml
<w:tr>
    <!-- 第 1 欄: Segment ID -->
    <w:tc>
        <w:p><w:r><w:t>7bb0408a-1</w:t></w:r></w:p>
    </w:tc>
    
    <!-- 第 2 欄: Status -->
    <w:tc>
        <w:p><w:r><w:t>Translated</w:t></w:r></w:p>
    </w:tc>
    
    <!-- 第 3 欄: Source -->
    <w:tc>
        <w:p><w:r><w:t>English source text</w:t></w:r></w:p>
    </w:tc>
    
    <!-- 第 4 欄: Target ⚠️ 我們要更新這個 -->
    <w:tc>
        <w:p>
            <!-- Tag 樣式（保留不動） -->
            <w:r>
                <w:rPr><w:rStyle w:val="Tag"/></w:rPr>
                <w:t>&lt;51&gt;</w:t> <!-- 純文本標籤 -->
            </w:r>
            
            <!-- 文本（要替換） -->
            <w:r>
                <w:t xml:space="preserve">中文翻譯</w:t>
            </w:r>
        </w:p>
    </w:tc>
</w:tr>
```

---

### Target cell 的典型結構

```xml
<w:tc>
    <w:p>
        <!-- 可能有多個 <w:r>，需要跳過 Tag 樣式 -->

        <!-- Tag 樣式 -->
        <w:r>
            <w:rPr>
                <w:rStyle w:val="Tag"/>
            </w:rPr>
            <w:t>&lt;51&gt;</w:t>
        </w:r>
        
        <!-- 普通文本（要替換） -->
        <w:r>
            <w:rPr>
                <!-- 可能有格式 -->
                <w:rFonts w:ascii="Arial"/>
                <w:sz w:val="24"/>
            </w:rPr>
            <w:t xml:space="preserve">實際翻譯文字</w:t>
        </w:r>
    </w:p>
</w:tc>
```

---

## 追蹤修訂結構

### 替換後的 Target cell 範例

```xml
<w:tc>
    <w:p>
        <!-- Tag 樣式（保留） -->
        <w:r>
            <w:rPr><w:rStyle w:val="Tag"/></w:rPr>
            <w:t>&lt;51&gt;</w:t>
        </w:r>
        
        <!-- 原文字被替換成追蹤修訂 -->
        
        <!-- 刪除標記 -->
        <w:del w:id="0" w:author="Claude" w:date="2024-01-01T00:00:00Z">
            <w:r w:rsidDel="00AB12CD">
                <w:rPr>
                    <!-- 保留原格式 -->
                </w:rPr>
                <w:delText>舊翻譯</w:delText>
            </w:r>
        </w:del>
        
        <!-- 插入標記 -->
        <w:ins w:id="1" w:author="Claude" w:date="2024-01-01T00:00:00Z">
            <w:r w:rsidR="00AB12CD">
                <w:rPr>
                    <!-- 保留原格式 -->
                </w:rPr>
                <w:t xml:space="preserve">新翻譯</w:t>
            </w:r>
        </w:ins>
    </w:p>
</w:tc>
```

> 💡 真實腳本會自動填充 `author`、`rsid`、`date`，以及原文字與新文字。

---

## 關鍵識別模式

### 如何識別 Tag 樣式

```python
rpr = run.getElementsByTagName("w:rPr")
if rpr:
    r_style = rpr[0].getElementsByTagName("w:rStyle")
    if r_style and r_style[0].getAttribute("w:val") == "Tag":
        # 這是 Tag 樣式，保留不動
        pass
```

---

### 如何保留格式

取出 `<w:rPr>` 的完整 XML，供追蹤修訂使用：

```python
rpr_tags = text_run.getElementsByTagName("w:rPr")
rpr = rpr_tags[0].toxml() if rpr_tags else ""

replacement = f'''<w:del>
    <w:r>
        {rpr}  <!-- 原格式 -->
        <w:delText>舊文字</w:delText>
    </w:r>
</w:del>
<w:ins>
    <w:r>
        {rpr}  <!-- 原格式 -->
        <w:t>新文字</w:t>
    </w:r>
</w:ins>'''
```

---

## 標籤保護（解決 `<51>` 衝突）

### 問題

Target cell 中的 `<51>`, `<52>` 等是純文本，看起來像 XML 標籤，查找時會報錯：

```python
node = doc.get_node(contains="<51>")  # ✗ XML 解析錯誤
```

### 解決方案

使用 Unicode 相似字符臨時保護：

```python
from scripts.tag_protector import protect_tags, restore_tags

text = "翻譯文字 <51>"
protected = protect_tags(text)  # → "翻譯文字 ⟨51⟩"

# 在 doc 內查找節點
node = doc.get_node(contains=protected)

# 更新文字...

# 最後統一恢復
doc.xml = restore_tags(doc.xml)
```

---

## 注意事項

1. 四欄結構，第 4 欄是 Target，必須更新此欄。
2. Target cell 可能有多個 `<w:r>`，要跳過 Tag 樣式。
3. 保留原 `<w:rPr>` 格式，確保追蹤修訂一致。
4. 標籤 `<51>`、`<52>` 等必須使用 `protect_tags()` 保護，避免 XML 解析錯誤。
5. 使用 Document 類別的 `replace_node()` 創建追蹤修訂，不要直接操作 XML 字串。
6. 真實更新中，author、rsid、date 由腳本自動生成。




