#!/usr/bin/env python3
"""
使用 Microsoft MarkItDown 提取 Word 表格（简化版）
只负责 Word → Markdown 转换，不做数据解析

用法:
    python extract_table_markitdown_simple.py input.docx output.md
"""

import sys
import argparse
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    print("错误：需要安装 markitdown")
    print("运行: pip install --user markitdown")
    sys.exit(1)


def extract_with_markitdown(docx_path: str, output_md: str) -> str:
    """
    使用 MarkItDown 将 Word 文档转换为 Markdown

    Args:
        docx_path: Word 文档路径
        output_md: 输出 Markdown 文件路径

    Returns:
        转换后的 Markdown 内容
    """
    print(f"使用 MarkItDown 读取: {docx_path}")

    md = MarkItDown()
    result = md.convert(docx_path)

    # 获取 Markdown 内容
    markdown_content = result.text_content

    # 写入文件
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"✓ Markdown 已保存: {output_md}")

    # 简单统计
    lines = markdown_content.split('\n')
    table_lines = [l for l in lines if l.strip().startswith('|')]
    print(f"✓ Markdown 包含 {len(table_lines)} 行表格内容")

    return markdown_content


def main():
    parser = argparse.ArgumentParser(
        description='使用 MarkItDown 将 Word 转换为 Markdown（纯转换，不解析数据）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 转换 Word 为 Markdown
  python extract_table_markitdown_simple.py input.docx output.md

职责:
  ✓ Word → Markdown 转换（使用 MarkItDown）
  ✗ 不负责解析表格数据（由 generate_translation_mapping.py 负责）

下一步:
  使用 generate_translation_mapping.py 来解析 Markdown 表格
        '''
    )

    parser.add_argument('input_docx', help='输入 Word 文档路径')
    parser.add_argument('output_md', help='输出 Markdown 文件路径')

    args = parser.parse_args()

    # 检查输入文件
    if not Path(args.input_docx).exists():
        print(f"✗ 错误：文件不存在 - {args.input_docx}")
        return 1

    print("=" * 80)
    print("Word → Markdown 转换器（MarkItDown）")
    print("=" * 80)

    try:
        # 提取表格
        markdown_content = extract_with_markitdown(args.input_docx, args.output_md)

        print("\n" + "=" * 80)
        print("✓ 转换完成！")
        print("=" * 80)
        print("\n下一步:")
        print(f"  1. 查看 Markdown: cat {args.output_md}")
        print(f"  2. 使用 generate_translation_mapping.py 解析表格")

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
