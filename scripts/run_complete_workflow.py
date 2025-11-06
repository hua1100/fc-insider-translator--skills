#!/usr/bin/env python3
"""
FC Insider 翻译更新 - 一键执行完整工作流程

功能：
1. 从 Word 文档提取表格（使用 MarkItDown）
2. 生成翻译映射（智能匹配）
3. 应用追踪修订到 Word 文档

使用方法：
python3 run_complete_workflow.py \\
  --input "input.docx" \\
  --new-translations "new_translations.txt" \\
  --output "output.docx" \\
  --author "Your Name" \\
  --verbose
"""

import argparse
import sys
import os
import subprocess
import tempfile
from pathlib import Path


def print_step(step_num, total_steps, description):
    """打印步骤信息"""
    print(f"\n{'='*80}")
    print(f"步骤 {step_num}/{total_steps}: {description}")
    print(f"{'='*80}\n")


def run_command(cmd, description, verbose=False):
    """
    运行命令并检查结果

    Args:
        cmd: 命令列表
        description: 命令描述
        verbose: 是否显示详细输出
    """
    print(f"→ {description}...")

    if verbose:
        print(f"  命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=not verbose,
            text=True
        )

        if not verbose and result.stdout:
            print(f"  {result.stdout.strip()}")

        print(f"✓ {description}完成")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ 错误：{description}失败")
        print(f"  退出码: {e.returncode}")
        if e.stdout:
            print(f"  输出: {e.stdout}")
        if e.stderr:
            print(f"  错误: {e.stderr}")
        return False


def check_dependencies():
    """检查必需的依赖"""
    print("\n检查依赖...")

    dependencies = {
        'markitdown': 'pip install markitdown',
        'python-docx': 'pip install python-docx',
        'lxml': 'pip install lxml'
    }

    missing = []

    for package, install_cmd in dependencies.items():
        try:
            if package == 'markitdown':
                __import__('markitdown')
            elif package == 'python-docx':
                __import__('docx')
            elif package == 'lxml':
                __import__('lxml')
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} 未安装")
            missing.append((package, install_cmd))

    if missing:
        print(f"\n⚠️  缺少依赖，需要安装：")
        for package, install_cmd in missing:
            print(f"  {install_cmd}")

        response = input("\n是否现在安装？(y/n): ")
        if response.lower() == 'y':
            for package, install_cmd in missing:
                print(f"\n安装 {package}...")
                subprocess.run(install_cmd.split(), check=True)
            print("\n✓ 所有依赖已安装")
        else:
            print("\n✗ 无法继续，请先安装依赖")
            return False

    return True


def get_script_path(script_name):
    """获取脚本的完整路径"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, script_name)


def main():
    parser = argparse.ArgumentParser(
        description='FC Insider 翻译更新 - 一键执行完整工作流程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  # 基本用法
  python3 run_complete_workflow.py \\
    --input "input.docx" \\
    --new-translations "new_translations.txt" \\
    --output "output.docx" \\
    --author "Gemini"

  # 详细模式
  python3 run_complete_workflow.py \\
    --input "input.docx" \\
    --new-translations "new_translations.txt" \\
    --output "output.docx" \\
    --author "Gemini" \\
    --verbose

  # 自定义匹配方式
  python3 run_complete_workflow.py \\
    --input "input.docx" \\
    --new-translations "new_translations.txt" \\
    --output "output.docx" \\
    --author "Gemini" \\
    --match-by index \\
    --update-mode read_inserted
        '''
    )

    parser.add_argument(
        '--input',
        required=True,
        help='输入 Word 文档路径'
    )
    parser.add_argument(
        '--new-translations',
        required=True,
        help='新翻译文件路径（纯文本或 JSON）'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='输出 Word 文档路径'
    )
    parser.add_argument(
        '--author',
        default='Claire',
        help='追踪修订作者名称（默认：Claire）'
    )
    parser.add_argument(
        '--match-by',
        choices=['smart', 'segment_id', 'index'],
        default='smart',
        help='匹配方式（默认：smart 智能匹配）'
    )
    parser.add_argument(
        '--update-mode',
        choices=['auto', 'read_deleted', 'read_inserted'],
        default='auto',
        help='更新模式（默认：auto 自动检测）'
    )
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='保留临时文件（用于调试）'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细输出'
    )
    parser.add_argument(
        '--skip-dependencies-check',
        action='store_true',
        help='跳过依赖检查（不推荐）'
    )

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"✗ 错误：输入文件不存在: {args.input}")
        return 1

    if not os.path.exists(args.new_translations):
        print(f"✗ 错误：新翻译文件不存在: {args.new_translations}")
        return 1

    print("="*80)
    print("FC Insider 翻译更新 - 一键执行工作流程")
    print("="*80)
    print(f"\n配置:")
    print(f"  输入文档: {args.input}")
    print(f"  新翻译: {args.new_translations}")
    print(f"  输出文档: {args.output}")
    print(f"  作者: {args.author}")
    print(f"  匹配方式: {args.match_by}")
    print(f"  更新模式: {args.update_mode}")

    # 检查依赖
    if not args.skip_dependencies_check:
        if not check_dependencies():
            return 1
    else:
        print("\n⚠️  跳过依赖检查")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix='fc_insider_')
    temp_table = os.path.join(temp_dir, 'extracted_table.md')
    temp_translations = os.path.join(temp_dir, 'translations.json')

    print(f"\n临时目录: {temp_dir}")

    try:
        # 步骤 1: 提取表格
        print_step(1, 3, "提取表格")

        extract_cmd = [
            'python3',
            get_script_path('extract_table_markitdown_simple.py'),
            args.input,
            temp_table
        ]

        if not run_command(extract_cmd, "提取表格", args.verbose):
            return 1

        # 步骤 2: 生成翻译映射
        print_step(2, 3, "生成翻译映射")

        mapping_cmd = [
            'python3',
            get_script_path('generate_translation_mapping.py'),
            '--markdown', temp_table,
            '--new-translations', args.new_translations,
            '--output', temp_translations,
            '--match-by', args.match_by
        ]

        if args.verbose:
            mapping_cmd.append('--verbose')

        if not run_command(mapping_cmd, "生成翻译映射", args.verbose):
            return 1

        # 步骤 3: 应用追踪修订
        print_step(3, 3, "应用追踪修订")

        update_cmd = [
            'python3',
            get_script_path('update_fc_insider_tracked.py'),
            '--input', args.input,
            '--translations', temp_translations,
            '--output', args.output,
            '--author', args.author,
            '--mode', args.update_mode
        ]

        if args.verbose:
            update_cmd.append('--verbose')

        if not run_command(update_cmd, "应用追踪修订", args.verbose):
            return 1

        # 完成
        print("\n" + "="*80)
        print("✓ 工作流程完成！")
        print("="*80)
        print(f"\n输出文档: {args.output}")

        if os.path.exists(args.output):
            file_size = os.path.getsize(args.output)
            print(f"文件大小: {file_size:,} 字节")

        return 0

    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # 清理临时文件
        if not args.keep_temp:
            import shutil
            try:
                shutil.rmtree(temp_dir)
                print(f"\n✓ 已清理临时文件")
            except Exception as e:
                print(f"\n⚠️  无法清理临时文件: {e}")
        else:
            print(f"\n保留临时文件:")
            print(f"  - 提取的表格: {temp_table}")
            print(f"  - 翻译映射: {temp_translations}")


if __name__ == '__main__':
    sys.exit(main())
