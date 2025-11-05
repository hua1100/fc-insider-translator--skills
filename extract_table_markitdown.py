#!/usr/bin/env python3
"""
使用 Microsoft MarkItDown 提取 Word 表格
MarkItDown 对表格的处理更准确，特别是复杂的表格结构

用法:
    python extract_table_markitdown.py input.docx output.md
    python extract_table_markitdown.py input.docx output.md --output-json table.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict
import re

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
    return markdown_content


def parse_markdown_tables(markdown_content: str) -> List[Dict[str, str]]:
    """
    从 Markdown 内容中解析表格

    Args:
        markdown_content: Markdown 文本内容

    Returns:
        提取的表格数据（列表形式）
    """
    rows_data = []
    lines = markdown_content.split('\n')

    in_table = False
    table_count = 0

    for i, line in enumerate(lines):
        line = line.strip()

        # 检测表格行
        if line.startswith('|') and line.endswith('|'):
            # 跳过分隔符行 (|---|---|---|)
            if re.match(r'^\|[\s\-:]+\|$', line):
                in_table = True
                table_count += 1
                print(f"  发现表格 {table_count}")
                continue

            # 跳过表头行（检查下一行是否为分隔符）
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if re.match(r'^\|[\s\-:]+\|$', next_line):
                    in_table = True
                    continue

            if in_table:
                # 解析数据行
                cells = [cell.strip() for cell in line.split('|')[1:-1]]

                # 跳过空行
                if all(not cell for cell in cells):
                    continue

                # FC Insider 格式：4 列
                if len(cells) >= 4:
                    rows_data.append({
                        'segment_id': cells[0],
                        'status': cells[1],
                        'source': cells[2],
                        'target': cells[3]
                    })
        elif in_table and line and not line.startswith('|'):
            # 表格结束
            in_table = False

    return rows_data


def main():
    parser = argparse.ArgumentParser(
        description='使用 MarkItDown 从 Word 文档提取表格',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 基本用法
  python extract_table_markitdown.py input.docx output.md

  # 同时生成 JSON
  python extract_table_markitdown.py input.docx output.md --output-json table.json

优势:
  ✓ 使用 Microsoft MarkItDown（专为 LLM 优化）
  ✓ 更准确的表格提取
  ✓ 保留文档结构
  ✓ 支持复杂表格
        '''
    )

    parser.add_argument('input_docx', help='输入 Word 文档路径')
    parser.add_argument('output_md', help='输出 Markdown 文件路径')
    parser.add_argument(
        '--output-json',
        help='可选：同时输出结构化 JSON 数据'
    )

    args = parser.parse_args()

    # 检查输入文件
    if not Path(args.input_docx).exists():
        print(f"✗ 错误：文件不存在 - {args.input_docx}")
        return 1

    print("=" * 80)
    print("Word 表格提取器（MarkItDown 版本）")
    print("=" * 80)

    try:
        # 提取表格
        markdown_content = extract_with_markitdown(args.input_docx, args.output_md)

        # 解析表格数据
        print("\n解析表格数据...")
        rows_data = parse_markdown_tables(markdown_content)

        print(f"✓ 共提取 {len(rows_data)} 行数据")

        # 预览前几行
        if rows_data:
            print("\n预览前 3 行:")
            for i, row in enumerate(rows_data[:3], 1):
                print(f"  [{i}] Segment: {row['segment_id'][:30]}")
                print(f"      Target: {row['target'][:50]}...")

        # 可选：保存 JSON
        if args.output_json:
            print(f"\n保存 JSON 数据: {args.output_json}")
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump({'rows': rows_data}, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON 已保存: {args.output_json} ({len(rows_data)} rows)")

        print("\n" + "=" * 80)
        print(f"✓ 完成！共提取 {len(rows_data)} 行数据")
        print("=" * 80)
        print("\n下一步:")
        print(f"  1. 查看 Markdown: cat {args.output_md}")
        print(f"  2. 使用 generate_translation_mapping.py 生成对照表")

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
