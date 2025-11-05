#!/usr/bin/env python3
"""
翻译对照表生成器

从 Markdown 表格和新译文生成新旧翻译对照表
输出格式与 update_fc_insider_v3.py 兼容

工作流程：
1. 读取从 Word 提取的 Markdown 表格
2. 读取新译文（可以是纯文本、JSON 或 AI 输出）
3. 生成 translations.json 对照表
4. 提供验证和预览功能
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional


def load_markdown_table(md_path: str) -> List[Dict[str, str]]:
    """
    从 Markdown 加载表格数据

    Returns:
        List of dicts with keys: segment_id, status, source, target
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rows = []
    in_table = False

    for line in lines:
        line = line.strip()

        if line.startswith('|') and line.endswith('|'):
            # 跳过分隔符
            if set(line.replace('|', '').replace('-', '').strip()) == set():
                in_table = True
                continue

            # 跳过表头
            if 'Segment ID' in line or 'segment_id' in line.lower():
                in_table = True
                continue

            if in_table:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) >= 4:
                    rows.append({
                        'segment_id': cells[0],
                        'status': cells[1],
                        'source': cells[2],
                        'target': cells[3]
                    })

    return rows


def load_new_translations(input_path: str, format: str = 'auto') -> Dict[str, str]:
    """
    加载新译文

    支持格式：
    - json: {"segment_id": "new_text", ...}
    - text: 按行分割的译文（与表格行对应）
    - auto: 自动检测
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 自动检测格式
    if format == 'auto':
        if content.strip().startswith('{'):
            format = 'json'
        else:
            format = 'text'

    if format == 'json':
        data = json.loads(content)
        # 支持多种 JSON 格式
        if isinstance(data, dict) and 'translations' in data:
            # 格式 1: {"translations": [{"segment_id": "...", "text": "..."}, ...]}
            return {
                item['segment_id']: item.get('text', item.get('new_text', ''))
                for item in data['translations']
            }
        elif isinstance(data, dict):
            # 格式 2: {"segment_id": "new_text", ...}
            return data
        else:
            raise ValueError("不支持的 JSON 格式")

    elif format == 'text':
        # 每行一个译文
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return {str(i): line for i, line in enumerate(lines)}

    else:
        raise ValueError(f"不支持的格式: {format}")


def generate_translation_mapping(
    old_table: List[Dict[str, str]],
    new_translations: Dict[str, str],
    match_by: str = 'segment_id'
) -> List[Dict[str, str]]:
    """
    生成新旧翻译对照表

    Args:
        old_table: 从 Word 提取的原始表格
        new_translations: 新译文（segment_id -> new_text）
        match_by: 匹配方式（'segment_id' 或 'index'）

    Returns:
        List of translation mappings for update_fc_insider_v3.py
    """
    mappings = []

    for idx, row in enumerate(old_table):
        segment_id = row['segment_id']
        old_text = row['target']

        # 匹配新译文
        if match_by == 'segment_id':
            new_text = new_translations.get(segment_id)
        elif match_by == 'index':
            new_text = new_translations.get(str(idx))
        else:
            raise ValueError(f"不支持的匹配方式: {match_by}")

        # 只有当新译文存在且与旧译文不同时才添加
        if new_text and new_text != old_text:
            mappings.append({
                'segment_id': segment_id,
                'old_text': old_text,
                'new_text': new_text
            })

    return mappings


def preview_changes(mappings: List[Dict[str, str]], limit: int = 10):
    """
    预览变更

    显示前 N 个变更以供人工验证
    """
    print("\n" + "=" * 80)
    print(f"变更预览（前 {min(limit, len(mappings))} 个，共 {len(mappings)} 个）")
    print("=" * 80)

    for i, mapping in enumerate(mappings[:limit], 1):
        seg_id = mapping['segment_id']
        old = mapping['old_text'][:100]  # 限制显示长度
        new = mapping['new_text'][:100]

        print(f"\n[{i}] {seg_id}")
        print(f"  旧: {old}{'...' if len(mapping['old_text']) > 100 else ''}")
        print(f"  新: {new}{'...' if len(mapping['new_text']) > 100 else ''}")

    if len(mappings) > limit:
        print(f"\n... 还有 {len(mappings) - limit} 个变更（省略显示）")


def validate_mappings(mappings: List[Dict[str, str]]) -> bool:
    """
    验证对照表的完整性

    检查：
    - segment_id 不为空
    - new_text 不为空
    - 没有重复的 segment_id
    """
    if not mappings:
        print("✗ 错误：对照表为空")
        return False

    seen_ids = set()
    errors = []

    for i, mapping in enumerate(mappings, 1):
        seg_id = mapping.get('segment_id', '').strip()
        new_text = mapping.get('new_text', '').strip()

        if not seg_id:
            errors.append(f"行 {i}: segment_id 为空")

        if not new_text:
            errors.append(f"行 {i} ({seg_id}): new_text 为空")

        if seg_id in seen_ids:
            errors.append(f"行 {i}: segment_id '{seg_id}' 重复")

        seen_ids.add(seg_id)

    if errors:
        print("✗ 验证失败:")
        for error in errors[:10]:  # 只显示前 10 个错误
            print(f"  • {error}")
        if len(errors) > 10:
            print(f"  ... 还有 {len(errors) - 10} 个错误")
        return False

    print("✓ 验证通过")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='生成新旧翻译对照表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 从 Markdown 表格和新译文 JSON 生成对照表
  python generate_translation_mapping.py \\
    --markdown table.md \\
    --new-translations new_trans.json \\
    --output translations.json

  # 预览变更而不保存
  python generate_translation_mapping.py \\
    --markdown table.md \\
    --new-translations new_trans.json \\
    --preview-only

  # 使用行索引匹配（当 segment_id 不可用时）
  python generate_translation_mapping.py \\
    --markdown table.md \\
    --new-translations new_trans.txt \\
    --match-by index \\
    --output translations.json
        '''
    )

    parser.add_argument(
        '--markdown',
        required=True,
        help='从 Word 提取的 Markdown 表格'
    )
    parser.add_argument(
        '--new-translations',
        required=True,
        help='新译文文件（JSON 或文本）'
    )
    parser.add_argument(
        '--output',
        default='translations.json',
        help='输出对照表路径（默认：translations.json）'
    )
    parser.add_argument(
        '--match-by',
        choices=['segment_id', 'index'],
        default='segment_id',
        help='匹配方式（默认：segment_id）'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'text', 'auto'],
        default='auto',
        help='新译文格式（默认：auto）'
    )
    parser.add_argument(
        '--preview-only',
        action='store_true',
        help='只预览变更，不保存文件'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("生成翻译对照表")
    print("=" * 80)

    # 加载数据
    print(f"\n读取 Markdown 表格: {args.markdown}")
    old_table = load_markdown_table(args.markdown)
    print(f"✓ 加载 {len(old_table)} 行")

    print(f"\n读取新译文: {args.new_translations}")
    new_translations = load_new_translations(args.new_translations, args.format)
    print(f"✓ 加载 {len(new_translations)} 个译文")

    # 生成对照表
    print(f"\n生成对照表（匹配方式: {args.match_by}）...")
    mappings = generate_translation_mapping(
        old_table,
        new_translations,
        match_by=args.match_by
    )
    print(f"✓ 生成 {len(mappings)} 个变更")

    # 验证
    if not validate_mappings(mappings):
        return 1

    # 预览
    preview_changes(mappings)

    # 保存
    if not args.preview_only:
        output_data = {'translations': mappings}
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 对照表已保存: {args.output}")
        print(f"\n下一步:")
        print(f"  python update_fc_insider_v3.py \\")
        print(f"    --unpacked <unpacked_dir> \\")
        print(f"    --translations {args.output} \\")
        print(f"    --rsid <rsid> \\")
        print(f"    --author 'Your Name'")
    else:
        print("\n(预览模式：未保存文件)")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
