---
name: aliyun-asr
description: 阿里云千问3-ASR-Flash 语音识别 Skill。支持北京和新加坡地域，识别本地语音文件（AMR/MP3/WAV等格式）。使用时先选择地域，然后只输出识别结果文本。
---

# 阿里云 ASR 语音识别 Skill

使用阿里云千问3-ASR-Flash 模型进行语音识别。

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

## 使用流程

**CRITICAL - 使用此 skill 时必须按以下步骤操作：**

1. 用户提供语音文件后，首先使用 AskUserQuestion 询问用户选择地域：
   - 北京地域
   - 新加坡地域
   - 美国地域

2. 然后询问用户提供**对应地域**的 API Key（完整格式如 `sk-xxx-your-key-here`）

3. 确认用户提供的是音频文件的**绝对路径**

4. 调用识别脚本：
   ```bash
   python3 ~/.claude/skills/aliyun-asr/recognize_amr.py --region [beijing|singapore|us] --api-key <API_KEY> <绝对路径>
   ```

5. 脚本只输出识别结果文本，直接展示给用户即可

## 直接使用命令示例

```bash
# 北京地域
python3 ~/.claude/skills/aliyun-asr/recognize_amr.py --region beijing --api-key sk-xxx /absolute/path/to/voice.amr

# 新加坡地域
python3 ~/.claude/skills/aliyun-asr/recognize_amr.py --region singapore --api-key sk-xxx /absolute/path/to/voice.amr
```

## 支持的音频格式

- AMR
- MP3
- WAV
- 其他阿里云 ASR 支持的格式

## 关键路径

Skill 目录：`~/.claude/skills/aliyun-asr/`

识别脚本：`~/.claude/skills/aliyun-asr/recognize_amr.py`
