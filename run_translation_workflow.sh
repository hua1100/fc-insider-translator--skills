#!/bin/bash
# FC Insider 翻译工作流程自动化脚本（混合方案）

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    cat << EOF
FC Insider 翻译工作流程自动化

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

工作流程:
  1. Word → Markdown（提取表格）
  2. 生成新旧翻译对照表
  3. 解包 Word 文档
  4. 应用追踪修订（XML 写入）
  5. 打包 Word 文档
  6. 清理临时文件

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
echo "FC Insider 翻译工作流程（混合方案）"
echo "=========================================="
echo "输入: $INPUT_DOCX"
echo "新译文: $NEW_TRANSLATIONS"
echo "输出: $OUTPUT_DOCX"
echo "作者: $AUTHOR"
echo "临时目录: $TEMP_DIR"
echo "=========================================="

# 阶段 1：提取表格
echo -e "\n${YELLOW}[1/6] 提取表格为 Markdown...${NC}"
python extract_table_to_markdown.py "$INPUT_DOCX" "$TEMP_DIR/table.md"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 提取失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 提取成功${NC}"

# 阶段 2：生成对照表
echo -e "\n${YELLOW}[2/6] 生成翻译对照表...${NC}"
python generate_translation_mapping.py \
  --markdown "$TEMP_DIR/table.md" \
  --new-translations "$NEW_TRANSLATIONS" \
  --output "$TEMP_DIR/translations.json"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 生成对照表失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 对照表生成成功${NC}"

# 阶段 3：解包 Word
echo -e "\n${YELLOW}[3/6] 解包 Word 文档...${NC}"
python /mnt/skills/public/docx/ooxml/scripts/unpack.py "$INPUT_DOCX" "$TEMP_DIR/unpacked/" > "$TEMP_DIR/unpack.log"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 解包失败${NC}"
    cat "$TEMP_DIR/unpack.log"
    exit 1
fi

RSID=$(grep "Suggested RSID" "$TEMP_DIR/unpack.log" | awk '{print $NF}')
if [ -z "$RSID" ]; then
    echo -e "${RED}✗ 无法获取 RSID${NC}"
    cat "$TEMP_DIR/unpack.log"
    exit 1
fi
echo -e "${GREEN}✓ 解包成功，RSID: $RSID${NC}"

# 阶段 4：应用追踪修订
echo -e "\n${YELLOW}[4/6] 应用追踪修订...${NC}"
python update_fc_insider_v3.py \
  --unpacked "$TEMP_DIR/unpacked/" \
  --translations "$TEMP_DIR/translations.json" \
  --rsid "$RSID" \
  --author "$AUTHOR"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 应用追踪修订失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 追踪修订应用成功${NC}"

# 阶段 5：打包 Word
echo -e "\n${YELLOW}[5/6] 打包 Word 文档...${NC}"
python /mnt/skills/public/docx/ooxml/scripts/pack.py \
  "$TEMP_DIR/unpacked/" \
  "$OUTPUT_DOCX"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 打包失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 打包成功${NC}"

# 验证输出
echo -e "\n${YELLOW}[6/6] 验证输出...${NC}"
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
echo "=========================================="
