#!/usr/bin/env python3
"""
清理新翻译文件格式

功能：
- 删除表格边框字符 │
- 删除行号
- 删除多余的空格
- 删除空行
- 验证内容完整性

用法:
    python clean_translation_text.py input.txt output.txt
    python clean_translation_text.py input.txt output.txt --verbose
"""

import sys
import argparse
import re
from pathlib import Path


def clean_line(line: str) -> str:
    """
    清理单行文本

    Args:
        line: 原始行

    Returns:
        清理后的行
    """
    # 1. 删除表格边框字符
    cleaned = line.replace('│', '')

    # 2. 删除开头的行号和空格（如 "    1 " 或 "1 "）
    cleaned = re.sub(r'^\s*\d+\s+', '', cleaned)

    # 3. 删除行首和行尾的空格
    cleaned = cleaned.strip()

    return cleaned


def is_placeholder_line(text: str) -> bool:
    """
    检测是否是占位符行

    Args:
        text: 文本内容

    Returns:
        是否是占位符
    """
    # 移除占位符和常见词后，剩余内容很少
    without_placeholders = re.sub(r'[<"]?\d+/?[>"]?', '', text)
    without_placeholders = re.sub(r'["""\'\'<>]', '', without_placeholders)
    without_placeholders = re.sub(r'(在第|頁|on page|page)', '', without_placeholders, flags=re.IGNORECASE)

    if len(without_placeholders.strip()) <= 3:
        return True

    # 包含多个占位符且文本很短
    placeholder_count = len(re.findall(r'<\d+/>', text))
    if placeholder_count >= 2 and len(text) <= 30:
        return True

    return False


def clean_translation_file(input_path: str, output_path: str, verbose: bool = False) -> dict:
    """
    清理翻译文件

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        verbose: 是否显示详细信息

    Returns:
        统计信息字典
    """
    stats = {
        'total_lines': 0,
        'empty_lines': 0,
        'placeholder_lines': 0,
        'cleaned_lines': 0,
        'truncated_lines': 0
    }

    cleaned_lines = []

    print(f"📖 读取文件: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stats['total_lines'] = len(lines)

    for idx, line in enumerate(lines, 1):
        # 清理行
        cleaned = clean_line(line)

        # 跳过空行
        if not cleaned:
            stats['empty_lines'] += 1
            if verbose:
                print(f"  [{idx}] 跳过空行")
            continue

        # 跳过占位符行
        if is_placeholder_line(cleaned):
            stats['placeholder_lines'] += 1
            if verbose:
                print(f"  [{idx}] 跳过占位符: {cleaned[:50]}...")
            continue

        # 检查是否被截断
        if cleaned.endswith('...') or cleaned.endswith('…'):
            stats['truncated_lines'] += 1
            if verbose:
                print(f"  ⚠️  [{idx}] 可能被截断: {cleaned[:50]}...")

        cleaned_lines.append(cleaned)
        stats['cleaned_lines'] += 1

        if verbose:
            print(f"  ✓ [{idx}] {cleaned[:50]}..." if len(cleaned) > 50 else f"  ✓ [{idx}] {cleaned}")

    # 写入输出文件
    print(f"\n💾 写入文件: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in cleaned_lines:
            f.write(line + '\n')

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='清理新翻译文件格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 基本用法
  python clean_translation_text.py input.txt output.txt

  # 详细模式
  python clean_translation_text.py input.txt output.txt --verbose

清理内容:
  - 删除表格边框字符 │
  - 删除行号（如 "1 ", "  3 "）
  - 删除多余的空格
  - 跳过空行
  - 跳过占位符行

输出:
  干净的翻译文本，每行一个翻译
        '''
    )

    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('output', help='输出文件路径')
    parser.add_argument('--verbose', action='store_true', help='显示详细信息')

    args = parser.parse_args()

    # 检查输入文件
    if not Path(args.input).exists():
        print(f"✗ 错误：文件不存在 - {args.input}")
        return 1

    print("=" * 80)
    print("翻译文件清理工具")
    print("=" * 80)
    print()

    try:
        # 清理文件
        stats = clean_translation_file(args.input, args.output, args.verbose)

        # 显示统计
        print("\n" + "=" * 80)
        print("✓ 清理完成！")
        print("=" * 80)
        print(f"\n统计:")
        print(f"  总行数: {stats['total_lines']}")
        print(f"  空行: {stats['empty_lines']}")
        print(f"  占位符行: {stats['placeholder_lines']}")
        print(f"  保留行数: {stats['cleaned_lines']}")

        if stats['truncated_lines'] > 0:
            print(f"\n⚠️  警告：{stats['truncated_lines']} 行可能被截断")
            print("   请检查这些行是否完整")

        print(f"\n输出文件: {args.output}")
        print(f"✓ 可以直接用于 generate_translation_mapping.py")

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
