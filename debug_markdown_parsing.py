#!/usr/bin/env python3
"""
诊断 Markdown 表格解析问题
帮助理解为什么提取 0 行数据
"""

import sys
import re
import argparse


def analyze_markdown(md_file: str):
    """分析 Markdown 文件的表格结构"""

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    print("=" * 80)
    print("Markdown 文件分析")
    print("=" * 80)

    # 1. 基本统计
    print(f"\n总行数: {len(lines)}")
    print(f"文件大小: {len(content)} 字符")

    # 2. 查找表格行
    table_lines = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('|') and line.strip().endswith('|'):
            table_lines.append((i, line))

    print(f"\n找到的表格行数: {len(table_lines)}")

    if not table_lines:
        print("\n⚠️  没有找到表格行！")
        print("\n前 30 行内容:")
        for i, line in enumerate(lines[:30], 1):
            print(f"{i:3d}: {line[:100]}")
        return

    # 3. 显示前几行表格
    print("\n前 10 行表格内容:")
    for i, (line_no, line) in enumerate(table_lines[:10], 1):
        print(f"第 {line_no} 行: {line[:100]}")

    # 4. 检测表格格式
    print("\n" + "=" * 80)
    print("表格格式检测")
    print("=" * 80)

    # 检查分隔符行
    separator_pattern = r'^\|[\s\-:]+\|$'
    separators = []
    for line_no, line in table_lines:
        if re.match(separator_pattern, line.strip()):
            separators.append((line_no, line))

    print(f"\n找到的分隔符行: {len(separators)}")
    if separators:
        print("分隔符示例:")
        for line_no, line in separators[:3]:
            print(f"  第 {line_no} 行: {line}")

    # 5. 分析列数
    print("\n" + "=" * 80)
    print("列数分析")
    print("=" * 80)

    column_counts = {}
    for line_no, line in table_lines:
        cells = line.split('|')
        # 去掉首尾的空元素
        cells = [c for c in cells if c.strip()]
        col_count = len(cells)
        column_counts[col_count] = column_counts.get(col_count, 0) + 1

    print("\n列数分布:")
    for col_count, count in sorted(column_counts.items()):
        print(f"  {col_count} 列: {count} 行")

    # 6. 提取数据行（跳过表头和分隔符）
    print("\n" + "=" * 80)
    print("数据行提取")
    print("=" * 80)

    data_rows = []
    in_table = False
    header_seen = False

    for i, line in enumerate(lines):
        line = line.strip()

        if not line.startswith('|') or not line.endswith('|'):
            if in_table:
                in_table = False
            continue

        # 检查是否是分隔符
        if re.match(separator_pattern, line):
            in_table = True
            header_seen = True
            print(f"✓ 在第 {i+1} 行找到表格分隔符")
            continue

        # 跳过表头
        if not header_seen and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(separator_pattern, next_line):
                print(f"✓ 在第 {i+1} 行找到表头")
                continue

        # 提取数据行
        if in_table or header_seen:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and any(cell for cell in cells):  # 不是空行
                data_rows.append((i+1, cells))

    print(f"\n提取的数据行: {len(data_rows)}")

    if data_rows:
        print("\n前 5 行数据:")
        for line_no, cells in data_rows[:5]:
            print(f"\n第 {line_no} 行 ({len(cells)} 列):")
            for j, cell in enumerate(cells):
                print(f"  列 {j+1}: {cell[:50]}")
    else:
        print("\n⚠️  没有提取到数据行！")
        print("\n可能的原因:")
        print("  1. 表格没有分隔符行（|---|---|---|）")
        print("  2. 表格格式不标准")
        print("  3. 表格内容为空")

    # 7. 建议
    print("\n" + "=" * 80)
    print("建议")
    print("=" * 80)

    if len(data_rows) == 0 and len(table_lines) > 0:
        print("\n✓ MarkItDown 成功生成了表格")
        print("✗ 但是解析逻辑未能识别数据行")
        print("\n请查看上面的表格内容，确认:")
        print("  1. 是否有分隔符行（|---|---|---|）？")
        print("  2. 表格格式是否标准？")
        print("\n如果格式不标准，需要调整 parse_markdown_tables 函数")


def main():
    parser = argparse.ArgumentParser(description='诊断 Markdown 表格解析问题')
    parser.add_argument('markdown_file', help='要分析的 Markdown 文件')

    args = parser.parse_args()

    try:
        analyze_markdown(args.markdown_file)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
