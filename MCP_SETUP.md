# MarkItDown MCP 配置指南

## 方案对比

### 方案 A：直接使用 Python API（推荐，已实现）

✅ **优势**：
- 无需额外配置
- 立即可用
- 性能更好（无网络开销）
- 更容易调试

**使用方法**：
```bash
python3 extract_table_markitdown.py input.docx output.md
```

### 方案 B：使用 MCP 服务器（可选）

✅ **优势**：
- 可以在多个客户端之间共享
- 标准化的协议
- 更容易与其他 MCP 工具集成

⚠️ **需要**：
- 配置 MCP 服务器
- 修改 Claude Desktop 配置（如果使用 Claude Desktop）

---

## 方案 A：Python API（推荐）

### 已经可以使用！

我已经创建了 `extract_table_markitdown.py`，它直接使用 MarkItDown 的 Python API。

```bash
# 基本用法
python3 extract_table_markitdown.py input.docx output.md

# 同时生成 JSON
python3 extract_table_markitdown.py input.docx output.md --output-json table.json
```

### 测试效果

```bash
# 测试提取
python3 extract_table_markitdown.py your_test_file.docx test_output.md

# 查看结果
cat test_output.md
```

---

## 方案 B：MCP 服务器配置

如果你确实需要使用 MCP 协议，以下是配置步骤：

### 步骤 1：安装 MCP 服务器

有几种选择：

#### 选项 1：官方 Microsoft MCP 服务器（如果有）

```bash
# 检查是否有官方 MCP 包
pip install markitdown-mcp
```

#### 选项 2：第三方 MCP 服务器

```bash
# KorigamiK 的实现
pip install --user markitdown-mcp-server

# 或者通过 npx（如果有 Node.js）
npx -y @smithery/cli install @KorigamiK/markitdown_mcp_server --client claude
```

### 步骤 2：配置 Claude Desktop

找到 Claude Desktop 配置文件：

**位置**：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**添加配置**：

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "python3",
      "args": ["-m", "markitdown_mcp"],
      "env": {}
    }
  }
}
```

或者使用 Docker：

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "markitdown-mcp:latest"
      ]
    }
  }
}
```

### 步骤 3：在 Claude Skills 中使用 MCP 工具

重启 Claude Desktop 后，你可以通过 MCP 协议调用工具：

```python
# 这是概念性代码，实际 API 可能不同
# Claude Desktop 会暴露 MCP 工具

# 调用 MCP 工具
result = mcp_client.call_tool(
    "markitdown",
    "convert_to_markdown",
    {"uri": "file:///path/to/document.docx"}
)
```

---

## 在 Claude Skills 环境中的推荐方案

### 当前环境检查

Claude Skills 环境中**没有 Claude Desktop 配置文件**，因此：

✅ **推荐：使用方案 A（Python API）**

原因：
1. 无需额外配置
2. 性能更好
3. 更容易调试
4. 已经创建并测试通过

### 如果确实需要 MCP

可以创建一个**本地 MCP 服务器包装器**：

```python
# mcp_markitdown_wrapper.py
"""本地 MCP 包装器，模拟 MCP 协议"""

from markitdown import MarkItDown

class MarkItDownMCP:
    def __init__(self):
        self.md = MarkItDown()

    def convert_to_markdown(self, uri: str) -> str:
        """
        MCP 兼容的接口

        Args:
            uri: file:// 或 http:// URI

        Returns:
            Markdown 内容
        """
        # 处理 file:// URI
        if uri.startswith('file://'):
            path = uri[7:]  # 移除 'file://'
            result = self.md.convert(path)
            return result.text_content

        # 处理 http:// 或 https:// URI
        elif uri.startswith('http'):
            result = self.md.convert_url(uri)
            return result.text_content

        else:
            raise ValueError(f"不支持的 URI 格式: {uri}")

# 使用示例
if __name__ == '__main__':
    mcp = MarkItDownMCP()
    result = mcp.convert_to_markdown('file:///path/to/document.docx')
    print(result)
```

---

## 性能对比

| 方案 | 启动时间 | 转换速度 | 内存占用 | 配置复杂度 |
|------|---------|---------|---------|-----------|
| Python API | < 1s | 快 | 低 | 无 |
| MCP (本地) | 1-2s | 中等 | 中等 | 中等 |
| MCP (Docker) | 2-5s | 中等 | 高 | 高 |

---

## 故障排查

### 问题 1：markitdown 未安装

```bash
pip install --user markitdown
```

### 问题 2：提取效果不好

```bash
# 使用详细模式查看更多信息
python3 -c "
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert('input.docx')
print('原始内容长度:', len(result.text_content))
print('前 500 字符:')
print(result.text_content[:500])
"
```

### 问题 3：MCP 服务器无法启动

```bash
# 检查 MCP 包是否安装
pip list | grep markitdown

# 手动测试 MCP 服务器
python3 -m markitdown_mcp
```

---

## 推荐工作流程

### 使用 Python API（当前推荐）

```bash
# 1. 提取表格
python3 extract_table_markitdown.py input.docx table.md

# 2. 生成对照表
python3 generate_translation_mapping.py \
  --markdown table.md \
  --new-translations new_trans.json \
  --output translations.json

# 3. 应用追踪修订
python3 update_fc_insider_simple.py \
  --input input.docx \
  --translations translations.json \
  --output output.docx
```

### 一键运行（需要更新脚本）

```bash
bash run_workflow_markitdown.sh input.docx new_trans.json output.docx
```

---

## 总结

### 立即可用（推荐）

✅ 使用 `extract_table_markitdown.py`（Python API）
- 无需配置
- 性能优秀
- 易于调试

### 未来可选（如需要）

⚠️ 配置 MCP 服务器
- 适合多客户端共享
- 标准化协议
- 需要额外配置

**建议**：先使用 Python API 方案测试效果，如果满足需求就不需要配置 MCP。

---

## 测试 MarkItDown 效果

```bash
# 测试你的 Word 文档
python3 extract_table_markitdown.py your_document.docx output.md

# 查看提取的表格
cat output.md

# 检查 Target segment 是否正确提取
grep "Target" output.md | head -5
```

如果效果好，就直接使用 Python API 方案！
