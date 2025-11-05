#!/bin/bash
# FC Insider 翻译工作流程（使用 MarkItDown）
# 使用 Microsoft MarkItDown 提供更准确的表格提取

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    cat << EOF
FC Insider 翻译工作流程（MarkItDown 版本）

用法:
  $0 <input.docx> <new_translations.json> [output.docx] [author]

参数:
  input.docx           输入 Word 文档
  new_translations.json 新译文文件（JSON 格式）
  output.docx          输出文档（可选，默认：output_with_tracking.docx）
  author               作者名称（可选，默认：Claude）

示例:
  $0 input.docx new_trans.json
  $0 input.docx new_trans.json output.docx "Your Name"

特点:
  ✓ 使用 Microsoft MarkItDown（更准确的表格提取）
  ✓ 专为 LLM 优化的文档转换
  ✓ 更好地处理复杂表格结构
  ✓ 完整的追踪修订支持

工作流程:
  1. 检查并安装依赖（markitdown, python-docx）
  2. 使用 MarkItDown 提取表格为 Markdown
  3. 生成新旧翻译对照表
  4. 应用追踪修订
  5. 保存输出文档

EOF
}

# 检查参数
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_help
    exit 0
fi

INPUT_DOCX="$1"
NEW_TRANSLATIONS="$2"
OUTPUT_DOCX="${3:-output_with_tracking.docx}"
AUTHOR="${4:-Claude}"

if [ -z "$INPUT_DOCX" ] || [ -z "$NEW_TRANSLATIONS" ]; then
    echo -e "${RED}错误：缺少必需参数${NC}"
    show_help
    exit 1
fi

# 检查文件是否存在
if [ ! -f "$INPUT_DOCX" ]; then
    echo -e "${RED}错误：文件不存在 - $INPUT_DOCX${NC}"
    exit 1
fi

if [ ! -f "$NEW_TRANSLATIONS" ]; then
    echo -e "${RED}错误：文件不存在 - $NEW_TRANSLATIONS${NC}"
    exit 1
fi

# 创建临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "=========================================="
echo -e "${BLUE}FC Insider 翻译工作流程（MarkItDown 版本）${NC}"
echo "=========================================="
echo "输入: $INPUT_DOCX"
echo "新译文: $NEW_TRANSLATIONS"
echo "输出: $OUTPUT_DOCX"
echo "作者: $AUTHOR"
echo "临时目录: $TEMP_DIR"
echo "=========================================="

# 阶段 0：检查依赖
echo -e "\n${YELLOW}[0/4] 检查依赖...${NC}"

# 检查 markitdown
python3 -c "from markitdown import MarkItDown" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}  安装 markitdown...${NC}"
    pip3 install --user markitdown > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 安装 markitdown 失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}  ✓ markitdown 已安装${NC}"
else
    echo -e "${GREEN}✓ markitdown 已安装${NC}"
fi

# 检查 python-docx
python3 -c "from docx import Document" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}  安装 python-docx...${NC}"
    pip3 install --user python-docx > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 安装 python-docx 失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}  ✓ python-docx 已安装${NC}"
else
    echo -e "${GREEN}✓ python-docx 已安装${NC}"
fi

# 阶段 1：提取表格（使用 MarkItDown）
echo -e "\n${YELLOW}[1/4] 使用 MarkItDown 提取表格...${NC}"
python3 extract_table_markitdown.py "$INPUT_DOCX" "$TEMP_DIR/table.md"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 提取失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 提取成功${NC}"

# 显示提取的表格预览
echo -e "${BLUE}表格预览（前 10 行）:${NC}"
head -20 "$TEMP_DIR/table.md" | grep -E "^\|" | head -10

# 阶段 2：生成对照表
echo -e "\n${YELLOW}[2/4] 生成翻译对照表...${NC}"
python3 generate_translation_mapping.py \
  --markdown "$TEMP_DIR/table.md" \
  --new-translations "$NEW_TRANSLATIONS" \
  --output "$TEMP_DIR/translations.json"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 生成对照表失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 对照表生成成功${NC}"

# 阶段 3：应用追踪修订
echo -e "\n${YELLOW}[3/4] 应用追踪修订...${NC}"
python3 update_fc_insider_simple.py \
  --input "$INPUT_DOCX" \
  --translations "$TEMP_DIR/translations.json" \
  --output "$OUTPUT_DOCX" \
  --author "$AUTHOR"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 应用追踪修订失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 追踪修订应用成功${NC}"

# 验证输出
echo -e "\n${YELLOW}[4/4] 验证输出...${NC}"
if [ -f "$OUTPUT_DOCX" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_DOCX" | cut -f1)
    echo -e "${GREEN}✓ 输出文件已生成: $OUTPUT_DOCX ($FILE_SIZE)${NC}"
else
    echo -e "${RED}✗ 输出文件不存在${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ 完成！${NC}"
echo "=========================================="
echo "输出文件: $OUTPUT_DOCX"
echo ""
echo "下一步:"
echo "  1. 在 Word 中打开文档查看追踪修订"
echo "  2. 审核所有变更"
echo "  3. 接受或拒绝修订"
echo ""
echo "提取的 Markdown 表格保留在: $TEMP_DIR/table.md"
echo "（注意：临时目录会在脚本结束时自动清理）"
echo "=========================================="
