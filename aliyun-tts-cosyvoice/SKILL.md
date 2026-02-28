---
name: aliyun-tts-cosyvoice
description: 阿里云 CosyVoice 声音复刻与语音合成 Skill，专门用于 CosyVoice 系列模型。支持声音复刻（创建自定义音色）和语音合成，支持北京和新加坡地域，支持系统音色和复刻音色。仅适用于 CosyVoice 系列模型，其他模型不适用。如使用千问 TTS 系列模型，请使用 aliyun-tts-qwen skill。
---

# 阿里云 CosyVoice 声音复刻与语音合成 Skill

## 概述

阿里云 CosyVoice 声音复刻与语音合成 Skill，专门用于 CosyVoice 系列模型。支持声音复刻（创建自定义音色）和语音合成，支持北京和新加坡地域，支持系统音色和复刻音色。

**仅适用于 CosyVoice 系列模型**，其他模型不适用。如使用千问 TTS 系列模型，请使用 aliyun-tts-qwen skill。

## 安全说明

- **无硬编码 API Key**：所有敏感信息由用户在使用时提供
- **无硬编码音频 URL**：音频 URL 由用户在使用时提供
- **无硬编码音色**：音色名称由用户在使用时提供
- **推荐使用环境变量**：API Key 可通过环境变量 `DASHSCOPE_API_KEY` 提供

## 前置条件

1. **获取 API Key**：在阿里云百炼平台获取 API Key
2. **安装依赖**：`pip install dashscope`
3. **音频 URL**：声音复刻需要音频文件是公网可访问的 URL

## 支持的模型

- `cosyvoice-v3-flash`（推荐）
- `cosyvoice-v3-plus`
- `cosyvoice-v2`
- `cosyvoice-v1`

## 声音复刻

### 创建音色

```bash
aliyun-tts-cosyvoice clone <audio_url> \
    --api-key <your_api_key> \
    --model cosyvoice-v3-flash \
    --prefix myvoice \
    --language zh
```

或使用环境变量：

```bash
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
aliyun-tts-cosyvoice clone <audio_url> \
    --model cosyvoice-v3-flash \
    --prefix myvoice
```

**参数说明：**
- `audio_url`: 公网可访问的音频文件 URL（必填）
- `--api-key`: 阿里云 API Key（必填，或通过环境变量提供）
- `--region`: 地域：`beijing`（北京）、`singapore`（新加坡）、`us`（美国），默认：`beijing`
- `--model`: 目标语音合成模型，默认：`cosyvoice-v3-flash`
- `--prefix`: 音色前缀（仅允许数字、大小写字母和下划线，不超过 10 个字符），默认：`myvoice`
- `--language`: 语言提示：`zh`、`en`、`fr`、`de`、`ja`、`ko`、`ru`、`pt`、`th`、`id`、`vi`（仅适用于 cosyvoice-v3-flash/plus）
- `--max-length`: 音频预处理后用于声音复刻的参考音频最大时长（秒），仅适用于 cosyvoice-v3-flash

**注意：**
- 创建音色后请保存好返回的 Voice ID，后续语音合成时需要使用
- 音色创建是异步的，需要等待部署完成（状态变为 OK）

### 查询音色列表

```bash
aliyun-tts-cosyvoice list \
    --api-key <your_api_key>
```

### 查询指定音色详情

```bash
aliyun-tts-cosyvoice query <voice_id> \
    --api-key <your_api_key>
```

### 删除音色

```bash
aliyun-tts-cosyvoice delete <voice_id> \
    --api-key <your_api_key>
```

## 语音合成

### 使用系统音色合成

```bash
aliyun-tts-cosyvoice synthesize "你好，今天天气怎么样？" \
    --api-key <your_api_key> \
    --model cosyvoice-v3-flash \
    --voice longanyang \
    --output /absolute/path/to/output.wav
```

### 使用复刻音色合成

```bash
aliyun-tts-cosyvoice synthesize "你好，今天天气怎么样？" \
    --api-key <your_api_key> \
    --model cosyvoice-v3-flash \
    --voice <voice_id> \
    --output /absolute/path/to/output.wav
```

**参数说明：**
- `text`: 待合成的文本（必填）
- `--api-key`: 阿里云 API Key（必填，或通过环境变量提供）
- `--region`: 地域：`beijing`（北京）、`singapore`（新加坡）、`us`（美国），默认：`beijing`
- `--model`: TTS 模型，默认：`cosyvoice-v3-flash`
- `--voice`: 音色名称（系统音色或复刻音色），可选
- `--output`: 输出音频文件路径（可选，需要绝对路径）

**注意：**
- 语音合成时使用的 `model` 必须与创建音色时的 `target_model` 完全一致
- `--output` 需要绝对路径

## 完整示例

### 端到端示例：从复刻到合成

```bash
# 1. 创建音色（需要公网音频 URL）
aliyun-tts-cosyvoice clone "https://example.com/audio.m4a" \
    --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
    --model cosyvoice-v3-flash \
    --prefix myvoice \
    --language zh

# 保存返回的 Voice ID，例如：cosyvoice-v3-flash-myvoice-xxxxxxxx

# 2. 使用复刻音色进行语音合成
aliyun-tts-cosyvoice synthesize "恭喜，已成功复刻并合成了属于自己的声音！" \
    --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
    --model cosyvoice-v3-flash \
    --voice cosyvoice-v3-flash-myvoice-xxxxxxxx \
    --output /absolute/path/to/output.wav
```

## 系统音色列表

CosyVoice 支持的系统音色请参考阿里云官方文档。

## 常见问题

### Q: 声音复刻需要什么格式的音频？

A: 支持 WAV (16bit)、MP3、M4A 格式，推荐 10~20 秒，最长不超过 60 秒。

### Q: 为什么语音合成失败？

A: 请检查：
1. 音色 ID 是否正确
2. 合成时使用的 model 是否与创建音色时的 target_model 完全一致
3. 音色状态是否为 OK

### Q: 可以使用本地音频文件进行声音复刻吗？

A: 不可以，声音复刻需要音频文件是公网可访问的 URL。您可以将音频文件上传到阿里云 OSS 或其他公网可访问的位置。

## 相关文档

- [CosyVoice 声音复刻官方文档](https://help.aliyun.com/zh/model-studio/cosyvoice-clone-api)
- [CosyVoice Python SDK 官方文档](https://help.aliyun.com/zh/model-studio/cosyvoice-python-sdk)
- [实时语音合成-CosyVoice/Sambert](https://help.aliyun.com/zh/model-studio/text-to-speech)
