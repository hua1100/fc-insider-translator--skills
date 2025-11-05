#!/usr/bin/env python3
"""
Word 表格提取器 - 将 FC Insider Word 表格转换为 Markdown
用于 AI 更容易理解和生成新旧翻译对照表

支持两种方法：
1. Pandoc（快速，推荐）
2. docx2python（精细控制）
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


def extract_with_pandoc(docx_path: str, output_md: str) -> bool:
    """
    使用 Pandoc 将 DOCX 转换为 Markdown

    Args:
        docx_path: Word 文档路径
        output_md: 输出 Markdown 文件路径

    Returns:
        True if successful, False otherwise
    """
    try:
        # 使用 GitHub Flavored Markdown 以获得更好的表格支持
        cmd = [
            'pandoc',
            docx_path,
            '-f', 'docx',
            '-t', 'gfm',  # GitHub Flavored Markdown
            '-o', output_md,
            '--wrap=none'  # 不自动换行，保持表格结构
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print(f"✓ Pandoc 转换成功: {output_md}")
        return True

    except FileNotFoundError:
        print("✗ 错误：未找到 Pandoc，请先安装：")
        print("  Ubuntu/Debian: sudo apt-get install pandoc")
        print("  macOS: brew install pandoc")
        return False

    except subprocess.CalledProcessError as e:
        print(f"✗ Pandoc 转换失败: {e.stderr}")
        return False


def extract_with_docx2python(docx_path: str, output_md: str) -> bool:
    """
    使用 docx2python 提取表格并转换为 Markdown

    这个方法提供更精细的控制，可以：
    - 过滤特定样式（如 "Tag" 样式）
    - 自定义表格格式
    - 提取元数据
    """
    try:
        from docx2python import docx2python
        from docx2python.iterators import iter_tables, is_tbl
    except ImportError:
        print("✗ 错误：未安装 docx2python，请运行：")
        print("  pip install docx2python")
        return False

    try:
        # 提取文档
        doc_result = docx2python(docx_path)

        # 生成 Markdown
        markdown_lines = ["# FC Insider Translation Table\n"]

        # 遍历所有表格
        for table_idx, table in enumerate(iter_tables(doc_result.document), 1):
            markdown_lines.append(f"## Table {table_idx}\n")

            # 转换表格为 Markdown
            if table:
                # 表头
                if len(table) > 0 and len(table[0]) >= 4:
                    header = "| Segment ID | Status | Source | Target |"
                    separator = "|------------|--------|--------|--------|"
                    markdown_lines.append(header)
                    markdown_lines.append(separator)

                # 数据行
                for row in table:
                    if len(row) >= 4:
                        # 清理单元格内容（移除多余空白）
                        cells = [clean_cell_text(cell) for cell in row[:4]]
                        row_md = "| " + " | ".join(cells) + " |"
                        markdown_lines.append(row_md)

            markdown_lines.append("")  # 表格之间空行

        # 写入文件
        with open(output_md, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))

        print(f"✓ docx2python 转换成功: {output_md}")
        return True

    except Exception as e:
        print(f"✗ docx2python 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def clean_cell_text(cell_content) -> str:
    """
    清理单元格内容
    - 移除多余空白
    - 处理嵌套列表
    - 保留换行为空格
    """
    if isinstance(cell_content, list):
        # 递归处理嵌套列表
        text_parts = []
        for item in cell_content:
            if isinstance(item, list):
                text_parts.extend(clean_cell_text(item) for item in item)
            else:
                text_parts.append(str(item).strip())
        return ' '.join(filter(None, text_parts))
    else:
        return str(cell_content).strip().replace('\n', ' ')


def parse_markdown_table(md_path: str) -> List[Dict[str, str]]:
    """
    解析 Markdown 表格，提取为结构化数据
    用于后续 AI 分析和生成对照表

    Returns:
        List of dicts with keys: segment_id, status, source, target
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rows = []
    in_table = False

    for line in lines:
        line = line.strip()

        # 检测表格行
        if line.startswith('|') and line.endswith('|'):
            # 跳过分隔符行
            if set(line.replace('|', '').replace('-', '').strip()) == set():
                in_table = True
                continue

            # 跳过表头
            if 'Segment ID' in line or 'segment_id' in line.lower():
                in_table = True
                continue

            if in_table:
                # 解析数据行
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) >= 4:
                    rows.append({
                        'segment_id': cells[0],
                        'status': cells[1],
                        'source': cells[2],
                        'target': cells[3]
                    })

    return rows


def main():
    parser = argparse.ArgumentParser(
        description='将 FC Insider Word 表格转换为 Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 使用 Pandoc（推荐，快速）
  python extract_table_to_markdown.py input.docx output.md

  # 使用 docx2python（精细控制）
  python extract_table_to_markdown.py input.docx output.md --method docx2python

  # 同时生成 JSON 结构化数据
  python extract_table_to_markdown.py input.docx output.md --output-json table.json
        '''
    )

    parser.add_argument('input_docx', help='输入 Word 文档路径')
    parser.add_argument('output_md', help='输出 Markdown 文件路径')
    parser.add_argument(
        '--method',
        choices=['pandoc', 'docx2python'],
        default='pandoc',
        help='转换方法（默认：pandoc）'
    )
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
    print(f"Word → Markdown 转换")
    print(f"输入: {args.input_docx}")
    print(f"输出: {args.output_md}")
    print(f"方法: {args.method}")
    print("=" * 80)

    # 执行转换
    if args.method == 'pandoc':
        success = extract_with_pandoc(args.input_docx, args.output_md)
    else:
        success = extract_with_docx2python(args.input_docx, args.output_md)

    if not success:
        return 1

    # 可选：生成 JSON
    if args.output_json:
        print("\n解析表格为 JSON...")
        try:
            rows = parse_markdown_table(args.output_md)
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump({'rows': rows}, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON 输出: {args.output_json} ({len(rows)} rows)")
        except Exception as e:
            print(f"✗ JSON 生成失败: {e}")
            return 1

    print("\n✓ 转换完成！")
    print("\n下一步:")
    print(f"  1. 查看 Markdown: cat {args.output_md}")
    print(f"  2. 让 AI 基于 Markdown 生成翻译对照表")
    print(f"  3. 使用 update_fc_insider_v3.py 应用追踪修订")

    return 0


if __name__ == '__main__':
    sys.exit(main())
