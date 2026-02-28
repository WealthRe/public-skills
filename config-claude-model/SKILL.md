---
name: config-claude-model
description: Claude Code 模型快速配置工具，自动同步更新 ~/.claude/settings.json 和 ~/.zshrc 配置文件
---

# Claude Code 模型配置技能

## 概述

这是一个用于快速配置 Claude Code AI 模型的技能。它可以自动检测并更新以下配置文件，确保设置一致且立即生效：

- **`~/.claude/settings.json`** - Claude Code 核心配置（最高优先级）
- **`~/.zshrc`** - 环境变量配置
- **`~/Library/Application Support/Code/User/settings.json`** - VSCode 插件配置（可选）

## 配置优先级

Claude Code 配置来源及优先级：

1. **`~/.claude/settings.json`** ⭐ (最高优先级，Claude Code 优先读取)
2. **环境变量** (`export ANTHROPIC_*`) - 在 `~/.zshrc` 中设置
3. **VSCode 插件配置** - 仅用于 VSCode 插件界面显示

## 核心功能

运行技能会自动：

1. ✅ 检查配置文件是否存在
2. ✅ 更新 `~/.claude/settings.json` 和 `~/.zshrc`
3. ✅ 检测到 VSCode 配置文件时，询问是否更新
4. ✅ 保持文件完整性，仅更新必要的配置项

## 使用方法

### 方式 1: 直接执行脚本（推荐）

```bash
cd ~/.claude/skills/config-claude-model/scripts
chmod +x config_claude_model.sh
./config_claude_model.sh \
  --base-url "https://coding.dashscope.aliyuncs.com/apps/anthropic" \
  --auth-token "sk-sp-your-token-here" \
  --model "qwen3-max-2026-01-23"
```

### 配置示例

#### 阿里千问 (DashScope)
```bash
./config_claude_model.sh \
  --base-url "https://coding.dashscope.aliyuncs.com/apps/anthropic" \
  --auth-token "sk-sp-your-token-here" \
  --model "qwen3-max-2026-01-23"
```

#### Kimi (Moonshot)
```bash
./config_claude_model.sh \
  --base-url "https://api.kimi.com/coding/" \
  --auth-token "sk-kimi-your-token-here" \
  --model "kimi-for-coding"
```

#### 深度求索 (DeepSeek)
```bash
./config_claude_model.sh \
  --base-url "https://api.deepseek.com/coding/" \
  --auth-token "sk-your-token-here" \
  --model "deepseek-v3.2"
```

#### 火山方舟 (VolcEngine)
```bash
./config_claude_model.sh \
  --base-url "https://ark.cn-beijing.volces.com/api/coding" \
  --auth-token "your-token-here" \
  --model "doubao-seed-code"
```

## 验证配置

### 检查当前生效的环境变量

```bash
env | grep ANTHROPIC
```

### 查看配置文件

```bash
cat ~/.claude/settings.json
cat ~/.zshrc | grep ANTHROPIC
```

## 使配置生效

更新配置后，需要重启 Claude Code：

1. 完全退出 Claude Code（Cmd+Q）
2. 重新启动 Claude Code
3. 或执行：`source ~/.zshrc` （仅对新终端窗口生效）

## 文件说明

- **`scripts/config_claude_model.sh`** - 主执行脚本
- **`references/usage.md`** - 详细使用文档
- **`assets/templates/`** - 配置模板文件
- **`SKILL.md`** - 技能描述文档（本文件）
