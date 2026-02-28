# Claude Code 模型配置技能 - 使用指南

## 快速开始

### 基本用法

```bash
cd ~/.claude/skills/config-claude-model/scripts
chmod +x config_claude_model.sh
./config_claude_model.sh --help
```

### 配置阿里千问模型

```bash
./config_claude_model.sh \
  --base-url "https://coding.dashscope.aliyuncs.com/apps/anthropic" \
  --auth-token "sk-sp-your-token-here" \
  --model "qwen3-max-2026-01-23"
```

## 参数说明

| 参数 | 是否必需 | 说明 | 示例 |
|------|----------|------|------|
| `--base-url` | ✅ | API 基础端点 | `https://coding.dashscope.aliyuncs.com/apps/anthropic` |
| `--auth-token` | ✅ | API 认证令牌 | `sk-sp-xxxxxxxxxxxxxxxxxxxx` |
| `--model` | ✅ | 模型名称 | `qwen3-max-2026-01-23` |
| `--help` | ❌ | 显示帮助信息 | `-` |

## 支持的模型配置

### 1. 阿里云千问 (DashScope)

**推荐模型：** `qwen3-max-2026-01-23`

```bash
./config_claude_model.sh \
  --base-url "https://coding.dashscope.aliyuncs.com/apps/anthropic" \
  --auth-token "sk-sp-your-token" \
  --model "qwen3-max-2026-01-23"
```

**其他可用模型：**
- `qwen3-coder-plus` - 代码优化版
- `qwen3-max` - 最大版
- `qwen3-plus` - 增强版

### 2. Kimi (Moonshot)

**推荐模型：** `kimi-for-coding`

```bash
./config_claude_model.sh \
  --base-url "https://api.kimi.com/coding/" \
  --auth-token "sk-kimi-your-token" \
  --model "kimi-for-coding"
```

### 3. 深度求索 (DeepSeek)

**推荐模型：** `deepseek-v3.2`

```bash
./config_claude_model.sh \
  --base-url "https://api.deepseek.com/coding/" \
  --auth-token "sk-your-token" \
  --model "deepseek-v3.2"
```

### 4. 火山引擎方舟

**推荐模型：** `claude-3-5-sonnet-20241022`

```bash
./config_claude_model.sh \
  --base-url "https://ark.cn-beijing.volces.com/api/v3" \
  --auth-token "sk-your-token" \
  --model "claude-3-5-sonnet-20241022"
```

## 配置验证

### 检查环境变量

```bash
env | grep ANTHROPIC
```

**预期输出：**
```
ANTHROPIC_BASE_URL=https://coding.dashscope.aliyuncs.com/apps/anthropic
ANTHROPIC_AUTH_TOKEN=sk-sp-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=qwen3-max-2026-01-23
```

### 查看配置文件

```bash
cat ~/.claude/settings.json
cat ~/.zshrc | grep ANTHROPIC
```

### 检查配置优先级

```bash
# settings.json 优先级最高
cat ~/.claude/settings.json | grep ANTHROPIC

# 然后是环境变量
env | grep ANTHROPIC

# 最后是 .zshrc 中的 export
grep -E "^export ANTHROPIC" ~/.zshrc
```

## 使配置生效

### 方法 1: 重启 Claude Code（推荐）

1. 完全退出 Claude Code (Cmd+Q)
2. 重新启动 Claude Code

### 方法 2: 重新加载 Shell 配置

```bash
source ~/.zshrc
```

**注意：** 此方法仅对新打开的终端窗口生效，Claude Code 仍需重启。

## 配置文件说明

### 1. `~/.claude/settings.json`

Claude Code **优先读取**此文件，配置优先级最高。

**自动创建的内容：**
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "ANTHROPIC_BASE_URL": "https://coding.dashscope.aliyuncs.com/apps/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-sp-xxxxxxxxxxxxxxxxxxxx",
    "ANTHROPIC_MODEL": "qwen3-max-2026-01-23"
  },
  "permissions": {
    "allow": [...],
    "defaultMode": "default"
  }
}
```

### 2. `~/.zshrc`

设置环境变量，用于命令行启动和新终端窗口。

**自动添加的内容：**
```bash
# Claude Code Model Configuration
export ANTHROPIC_BASE_URL="https://coding.dashscope.aliyuncs.com/apps/anthropic"
export ANTHROPIC_AUTH_TOKEN="sk-sp-xxxxxxxxxxxxxxxxxxxx"
export ANTHROPIC_MODEL="qwen3-max-2026-01-23"
```

## 常见问题

### Q1: 配置后没有生效？

**解决方案：**
1. 确认已重启 Claude Code
2. 检查 `env | grep ANTHROPIC` 看配置是否正确
3. 查看 `~/.claude/settings.json` 文件内容

### Q2: 如何切换回之前的模型？

**解决方案：**
直接重新运行脚本，传入新的模型参数即可。脚本会自动覆盖旧配置。

```bash
./config_claude_model.sh \
  --base-url "https://api.kimi.com/coding/" \
  --auth-token "sk-kimi-xxx" \
  --model "kimi-for-coding"
```

### Q3: 可以在多个终端中使用不同的模型吗？

**解决方案：**
可以。在某个终端中临时修改环境变量：

```bash
# 仅对当前终端生效
export ANTHROPIC_MODEL="qwen3-plus"
export ANTHROPIC_BASE_URL="https://coding.dashscope.aliyuncs.com/apps/anthropic"
export ANTHROPIC_AUTH_TOKEN="sk-sp-xxx"
```

### Q4: 脚本提示找不到 jq 工具？

**解决方案：**
脚本会自动降级为重新创建 `settings.json`，不影响使用。如果想安装 jq：

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt install jq

# CentOS/RHEL
sudo yum install jq
```

### Q5: 如何备份当前配置？

**解决方案：**
在运行脚本前，手动备份：

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.backup
cp ~/.zshrc ~/.zshrc.backup
```

## 故障排除

### 配置文件权限问题

```bash
# 检查文件权限
ls -la ~/.claude/settings.json
ls -la ~/.zshrc

# 修复权限（如果需要）
chmod 644 ~/.claude/settings.json
chmod 644 ~/.zshrc
```

### 脚本执行权限

```bash
# 添加执行权限
chmod +x ~/.claude/skills/config-claude-model/scripts/config_claude_model.sh
```

### Claude Code 读取了错误的配置

**检查优先级：**
1. `~/.claude/settings.json` (最高)
2. 环境变量 (通过 `env` 命令查看)
3. `~/.zshrc` 中的 export

**清理方法：**
```bash
# 删除 settings.json（谨慎！）
rm ~/.claude/settings.json

# 重新运行配置脚本
./config_claude_model.sh --base-url ... --auth-token ... --model ...
```

## 安全提示

1. **不要**在公共场合泄露您的 API Token
2. **定期**更换 API Token 以确保安全
3. **使用**环境变量管理敏感信息，避免硬编码
4. **备份**配置文件，便于回滚

## 更多信息

- **项目地址：** `~/.claude/skills/config-claude-model/`
- **主文档：** `SKILL.md`
- **脚本位置：** `scripts/config_claude_model.sh`
- **配置文件：** `~/.claude/settings.json`
