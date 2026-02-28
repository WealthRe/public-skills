# Claude Code 模型配置示例

## 阿里云千问 (DashScope)

```bash
./config_claude_model.sh \
  --base-url "https://coding.dashscope.aliyuncs.com/apps/anthropic" \
  --auth-token "sk-sp-your-token-here" \
  --model "qwen3-max-2026-01-23"
```

## Kimi (Moonshot)

```bash
./config_claude_model.sh \
  --base-url "https://api.kimi.com/coding/" \
  --auth-token "sk-kimi-your-token-here" \
  --model "kimi-for-coding"
```

## 深度求索 (DeepSeek)

```bash
./config_claude_model.sh \
  --base-url "https://api.deepseek.com/coding/" \
  --auth-token "sk-your-token-here" \
  --model "deepseek-v3.2"
```

## 火山引擎方舟

```bash
./config_claude_model.sh \
  --base-url "https://ark.cn-beijing.volces.com/api/v3" \
  --auth-token "sk-your-token-here" \
  --model "claude-3-5-sonnet-20241022"
```

## 验证配置

```bash
# 检查环境变量
env | grep ANTHROPIC

# 查看配置文件
cat ~/.claude/settings.json
cat ~/.zshrc | grep ANTHROPIC
```

## 使配置生效

```bash
# 重启 Claude Code 或重新加载配置
source ~/.zshrc
```
