#!/bin/bash

# Claude Code 模型配置脚本
# 自动更新 ~/.claude/settings.json、~/.zshrc 和 VSCode settings.json

set -e

# 配置路径
claude_dir="$HOME/.claude"
vscode_settings="$HOME/Library/Application Support/Code/User/settings.json"
zshrc_file="$HOME/.zshrc"

# 显示帮助信息
show_help() {
    cat <<EOF
Claude Code 模型配置工具

用法:
  ./config_claude_model.sh [选项]

选项:
  --base-url <URL>        API 基础端点 (必需)
  --auth-token <TOKEN>    认证令牌 (必需)
  --model <MODEL_NAME>    模型名称 (必需)
  --help                  显示此帮助信息

示例:
  ./config_claude_model.sh \\
    --base-url "https://coding.dashscope.aliyuncs.com/apps/anthropic" \\
    --auth-token "sk-sp-your-token-here" \\
    --model "qwen3-max-2026-01-23"

支持的模型配置:
  - 阿里千问 (DashScope): qwen3-max-2026-01-23, qwen3-coder-plus
  - Kimi (Moonshot): kimi-for-coding
  - DeepSeek: deepseek-v3.2
  - 火山方舟 (VolcEngine): doubao-seed-code, claude-3-5-sonnet
EOF
}

# 解析参数
base_url=""
auth_token=""
model=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --base-url)
            base_url="$2"
            shift 2
            ;;
        --auth-token)
            auth_token="$2"
            shift 2
            ;;
        --model)
            model="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证必需参数
if [ -z "$base_url" ] || [ -z "$auth_token" ] || [ -z "$model" ]; then
    echo "错误: 缺少必需参数"
    echo ""
    show_help
    exit 1
fi

echo "=== Claude Code 模型配置 ==="
echo "Base URL: $base_url"
echo "Model: $model"
echo ""

# 检查文件存在性
echo "📁 检查配置文件..."

# 创建 .claude 目录（如果不存在）
mkdir -p "$claude_dir"

files_to_update=()
if [ -f "$claude_dir/settings.json" ]; then
    echo "✅ 检测到 ~/.claude/settings.json"
    files_to_update+=("$claude_dir/settings.json")
else
    echo "⚠️  未找到 ~/.claude/settings.json，将创建新文件"
    files_to_update+=("$claude_dir/settings.json")
fi

if [ -f "$zshrc_file" ]; then
    echo "✅ 检测到 ~/.zshrc"
    files_to_update+=("$zshrc_file")
else
    echo "⚠️  未找到 ~/.zshrc，将跳过更新"
fi

# 检查 VSCode 配置
vscode_update=false
if [ -f "$vscode_settings" ]; then
    echo "✅ 检测到 VSCode settings.json"
    echo ""

    # 询问是否更新 VSCode 配置
    read -p "❓ 是否更新 VSCode 插件配置 (claudeCode.selectedModel)? [Y/n]: " vscode_choice
    vscode_choice=${vscode_choice:-Y}

    if [[ "$vscode_choice" =~ ^[Yy]$ ]]; then
        echo "✅ 将更新 VSCode 配置"
        vscode_update=true
        files_to_update+=("$vscode_settings")
    else
        echo "⏭️  跳过更新 VSCode 配置"
    fi
else
    echo "⚠️  未找到 VSCode settings.json，将跳过更新"
fi

echo ""
echo "🔄 开始更新 ${#files_to_update[@]} 个配置文件..."
echo ""

# 更新 settings.json
if [[ " ${files_to_update[@]} " =~ " $claude_dir/settings.json " ]]; then
    echo "🔄 正在更新 $claude_dir/settings.json..."

    if command -v jq &> /dev/null && [ -f "$claude_dir/settings.json" ]; then
        # 使用 jq 更新现有配置
        tmp_file=$(mktemp)
        jq --arg url "$base_url" \
           --arg token "$auth_token" \
           --arg model "$model" \
           '.env.ANTHROPIC_BASE_URL = $url |
            .env.ANTHROPIC_AUTH_TOKEN = $token |
            .env.ANTHROPIC_MODEL = $model' \
           "$claude_dir/settings.json" > "$tmp_file"
        mv "$tmp_file" "$claude_dir/settings.json"
        echo "✅ settings.json 已更新"
    else
        # 创建或覆盖配置文件
        cat > "$claude_dir/settings.json" <<EOF
{
  "\$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "ANTHROPIC_BASE_URL": "$base_url",
    "ANTHROPIC_AUTH_TOKEN": "$auth_token",
    "ANTHROPIC_MODEL": "$model"
  },
  "permissions": {
    "allow": [
      "Read", "Edit", "Write", "Glob", "Grep", "NotebookEdit", "Bash",
      "Task", "TaskOutput", "TaskStop", "TaskCreate", "TaskUpdate",
      "TaskList", "TaskGet", "WebFetch", "WebSearch", "AskUserQuestion",
      "EnterPlanMode", "ExitPlanMode", "Skill", "mcp__pencil__*"
    ],
    "defaultMode": "default"
  }
}
EOF
        echo "✅ settings.json 已创建/更新"
    fi
fi

# 更新 .zshrc
if [[ " ${files_to_update[@]} " =~ " $zshrc_file " ]]; then
    echo "🔄 正在更新 $zshrc_file..."

    # 读取 .zshrc 内容
    zshrc_content=$(cat "$zshrc_file" 2>/dev/null || echo "")

    # 移除已存在的 ANTHROPIC_* 变量
    zshrc_content=$(echo "$zshrc_content" | sed '/^export ANTHROPIC_/d')

    # 添加新的环境变量
    new_exports="
# Claude Code Model Configuration
export ANTHROPIC_BASE_URL=\"$base_url\"
export ANTHROPIC_AUTH_TOKEN=\"$auth_token\"
export ANTHROPIC_MODEL=\"$model\"
"

    # 写入文件
    echo "$zshrc_content$new_exports" > "$zshrc_file"
    echo "✅ .zshrc 已更新"
fi

# 更新 VSCode 配置
if [ "$vscode_update" = true ]; then
    echo "🔄 正在更新 VSCode settings.json..."

    if command -v jq &> /dev/null; then
        tmp_file=$(mktemp)
        jq --arg model "$model" \
           '. + {"claudeCode.selectedModel": $model}' \
           "$vscode_settings" > "$tmp_file"
        mv "$tmp_file" "$vscode_settings"
        echo "✅ VSCode settings.json 已更新 (claudeCode.selectedModel=\"$model\")"
    else
        echo "⚠️  未找到 jq 工具，无法更新 VSCode 配置"
        echo "   请手动在 VSCode settings.json 中设置: \"claudeCode.selectedModel\": \"$model\""
    fi
fi

echo ""
echo "🎉 Claude Code 模型配置更新完成！"
echo ""
echo "📌 配置摘要:"
echo "   - Base URL: $base_url"
echo "   - Model: $model"
echo ""
echo "⚠️  请执行以下操作使配置生效:"
echo "   1. 完全退出 Claude Code (Cmd+Q)"
echo "   2. 重新启动 Claude Code"
echo "   3. 打开新终端: source ~/.zshrc"
echo ""
echo "🔍 验证配置:"
echo "   env | grep ANTHROPIC"
