---
name: aliyun-tts
description: 阿里云千问 TTS 语音合成 Skill。支持声音复刻和语音合成，支持北京和新加坡地域，支持系统音色和复刻音色。
---

# 阿里云 TTS 语音合成 Skill

使用阿里云千问 TTS 模型进行声音复刻和语音合成。

## 支持的地域

| 地域 | API URL | 说明 |
|------|---------|------|
| 北京 | `https://dashscope.aliyuncs.com/api/v1` | 中国内地 |
| 新加坡 | `https://dashscope-intl.aliyuncs.com/api/v1` | 国际版（亚太） |
| 美国 | `https://dashscope-intl.aliyuncs.com/api/v1` | 国际版（美洲） |

**重要提示**：
- 北京地域需要使用**北京地域的 API Key**
- 新加坡/美国地域需要使用**国际版 API Key**
- **不同地域的 Key 不能混用**

## 支持的模型

### 声音复刻目标模型

| 模型 | 说明 | 合成方式 |
|------|------|----------|
| qwen3-tts-vc-2026-01-22 | 千问3-TTS-VC | 非流式（推荐） |
| qwen3-tts-vc-realtime-2026-01-15 | 千问3-TTS-VC-Realtime | 双向流式 |

### 语音合成模型

| 模型 | 说明 |
|------|------|
| qwen3-tts-flash | 千问3-TTS-Flash（系统音色） |
| qwen3-tts-vc-2026-01-22 | 千问3-TTS-VC（声音复刻） |

## 使用流程

### 1. 声音复刻

用户提供音频文件后：
1. 询问用户选择地域（北京/新加坡/美国）
2. 询问用户提供**对应地域**的 API Key（完整格式如 `sk-xxx-your-key-here`）
3. 询问用户目标模型（推荐 qwen3-tts-vc-2026-01-22）
4. 询问用户音色名称
5. 确认音频文件是绝对路径
6. 调用复刻脚本

```bash
python3 ~/.claude/skills/aliyun-tts/voice_cloning.py create <音频文件绝对路径> \
    --region [beijing|singapore|us] \
    --api-key <API_KEY> \
    --model <目标模型> \
    --name <音色名称>
```

### 2. 查询音色列表

```bash
python3 ~/.claude/skills/aliyun-tts/voice_cloning.py list \
    --region [beijing|singapore|us] \
    --api-key <API_KEY>
```

### 3. 语音合成

用户提供文本后：
1. 询问用户选择地域（北京/新加坡/美国）
2. 询问用户提供**对应地域**的 API Key（完整格式如 `sk-xxx-your-key-here`）
3. 询问用户使用的模型
4. 询问用户音色名称（系统音色或复刻音色）
5. 可选：询问输出文件路径（需要绝对路径）
6. 调用合成脚本

```bash
python3 ~/.claude/skills/aliyun-tts/voice_synthesis.py synthesize "<文本>" \
    --region [beijing|singapore|us] \
    --api-key <API_KEY> \
    --model <模型> \
    --voice <音色名称> \
    --output <输出文件路径>
```

### 4. 列出系统音色

```bash
python3 ~/.claude/skills/aliyun-tts/voice_synthesis.py list-voices
```

## 直接使用命令示例

### 声音复刻

```bash
# 北京地域，使用非流式模型
python3 ~/.claude/skills/aliyun-tts/voice_cloning.py create \
    /absolute/path/to/voice.m4a \
    --region beijing \
    --api-key sk-xxx \
    --model qwen3-tts-vc-2026-01-22 \
    --name my_voice
```

### 语音合成

```bash
# 使用系统音色
python3 ~/.claude/skills/aliyun-tts/voice_synthesis.py synthesize "你好" \
    --region beijing \
    --api-key sk-xxx \
    --model qwen3-tts-flash \
    --voice Cherry \
    --output /absolute/path/to/output.wav

# 使用复刻音色（模型必须与创建时一致）
python3 ~/.claude/skills/aliyun-tts/voice_synthesis.py synthesize "你好" \
    --region beijing \
    --api-key sk-xxx \
    --model qwen3-tts-vc-2026-01-22 \
    --voice qwen-tts-vc-my_voice-xxx \
    --output /absolute/path/to/output.wav
```

## 音频文件要求

- 格式：WAV / MP3 / M4A / AAC / OGG
- 时长：10-20秒，不超过60秒
- 采样率：≥24kHz
- 声道：单声道
- 其他：无背景噪音，语音清晰

## 关键路径

Skill 目录：`~/.claude/skills/aliyun-tts/`

声音复刻脚本：`~/.claude/skills/aliyun-tts/voice_cloning.py`

语音合成脚本：`~/.claude/skills/aliyun-tts/voice_synthesis.py`
