#!/usr/bin/env python3
"""
標籤保護工具

將 <51>, <52> 等看起來像 XML 標籤的純文本
轉換為安全的 Unicode 字符，避免 XML 解析衝突
"""

def protect_tags(text):
    """
    將 < 和 > 替換為 Unicode 相似字符
    
    使用：
    - ⟨ (U+27E8 MATHEMATICAL LEFT ANGLE BRACKET)
    - ⟩ (U+27E9 MATHEMATICAL RIGHT ANGLE BRACKET)
    
    優點：
    1. 不是 XML 特殊字符
    2. 視覺上相似
    3. 不需要 HTML 實體編碼
    4. 避免二次轉義問題
    """
    if not text:
        return text
    
    return text.replace('<', '⟨').replace('>', '⟩')


def restore_tags(text):
    """
    恢復原始的 < 和 > 字符
    """
    if not text:
        return text
    
    return text.replace('⟨', '<').replace('⟩', '>')


def is_protected(text):
    """
    檢查文本是否已經被保護
    """
    return '⟨' in text or '⟩' in text


# 測試
if __name__ == '__main__':
    test_cases = [
        "這是 <51> 一個測試 <52>",
        "包含多個 <1> <2> <3> 標籤",
        "<100>開頭的標籤",
        "結尾的標籤<200>",
        "正常文本沒有標籤"
    ]
    
    print("標籤保護測試:")
    print("=" * 60)
    
    for text in test_cases:
        protected = protect_tags(text)
        restored = restore_tags(protected)
        
        print(f"原文: {text}")
        print(f"保護: {protected}")
        print(f"恢復: {restored}")
        print(f"驗證: {'✓' if text == restored else '✗'}")
        print("-" * 60)
