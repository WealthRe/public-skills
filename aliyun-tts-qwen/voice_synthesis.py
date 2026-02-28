#!/usr/bin/env python3
"""
阿里云千问语音合成脚本
支持使用系统音色或复刻音色进行语音合成
使用 requests 直接调用 API
"""

import os
import sys
import argparse
import base64
import requests


# API 配置
REGIONS = {
    "beijing": {
        "api_url": "https://dashscope.aliyuncs.com/api/v1"
    },
    "singapore": {
        "api_url": "https://dashscope-intl.aliyuncs.com/api/v1"
    },
    "us": {
        "api_url": "https://dashscope-intl.aliyuncs.com/api/v1"
    }
}

# 系统音色列表
SYSTEM_VOICES = {
    "zh": ["Cherry", "Zhiming", "Xiaoyan", "Xiaofeng", "Aixia", "Aimei", "Aiyu", "Aiya", "Aijing", "Nanbei"],
    "en": ["Emily", "Harry", "Olivia", "George"],
    "ja": ["Naoki", "Kana"],
    "ko": ["Sunwoo", "Jiyoung"]
}


def synthesize_text(text, api_key, region="beijing",
                    model="qwen3-tts-flash",
                    voice="Cherry", language_type="Chinese",
                    output_file=None, stream=False):
    """
    语音合成

    Args:
        text: 待合成的文本
        api_key: 阿里云 API Key
        region: 地域: beijing 或 singapore
        model: TTS模型名称
        voice: 音色名称（系统音色或复刻音色）
        language_type: 文本语种 (Chinese, English, Japanese, Korean)
        output_file: 输出音频文件路径（如果需要保存音频）
        stream: 是否流式输出
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    # 构建API URL
    base_url = config["api_url"]

    print(f"正在合成语音...")
    print(f"文本: {text}")
    print(f"模型: {model}")
    print(f"音色: {voice}")
    print(f"语种: {language_type}")
    print("-" * 60)

    # 使用 MultiModalConversation 的方式
    try:
        import dashscope
        dashscope.base_http_api_url = base_url

        response = dashscope.MultiModalConversation.call(
            model=model,
            api_key=api_key,
            text=text,
            voice=voice,
            language_type=language_type,
            stream=stream
        )

        # 尝试不同的方式解析响应
        audio_url = None

        if hasattr(response, 'output'):
            # 对象方式访问
            output = response.output
            if hasattr(output, 'audio') and output.audio:
                if hasattr(output.audio, 'url'):
                    audio_url = output.audio.url
            elif hasattr(output, 'choices') and output.choices:
                choice = output.choices[0]
                if hasattr(choice, 'message'):
                    message = choice.message
                    if hasattr(message, 'content') and message.content:
                        for item in message.content:
                            if hasattr(item, 'audio'):
                                audio_url = item.audio
                            elif hasattr(item, 'text'):
                                print(f"响应文本: {item.text}")
        elif isinstance(response, dict):
            # 字典方式访问
            output = response.get('output', {})
            if output:
                audio = output.get('audio', {})
                if audio:
                    audio_url = audio.get('url')
                if not audio_url:
                    choices = output.get('choices', [])
                    if choices:
                        message = choices[0].get('message', {})
                        if message:
                            content = message.get('content', [])
                            if content:
                                for item in content:
                                    if item and 'audio' in item:
                                        audio_url = item['audio']
                                    elif item and 'text' in item:
                                        print(f"响应文本: {item['text']}")

        if audio_url:
            print("语音合成成功！")
            print(f"音频URL: {audio_url}")
            return save_audio_from_url(audio_url, output_file)
        else:
            print("未能从响应中提取音频数据")
            return None

    except Exception as e:
        print(f"语音合成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def save_audio_from_url(audio_url, output_file):
    """从URL下载并保存音频"""
    if output_file:
        try:
            response = requests.get(audio_url)
            response.raise_for_status()

            with open(output_file, 'wb') as f:
                f.write(response.content)

            print(f"音频已保存到: {output_file}")
            return response.content
        except Exception as e:
            print(f"下载音频失败: {e}")
            return None
    else:
        print("音频URL:")
        print(audio_url)
        return audio_url


def save_audio(audio_data, output_file):
    """保存音频数据到文件"""
    if output_file:
        import base64
        if audio_data.startswith('data:'):
            # Data URL 格式，提取 base64 部分
            base64_str = audio_data.split(',')[1]
        else:
            base64_str = audio_data

        audio_bytes = base64.b64decode(base64_str)

        with open(output_file, 'wb') as f:
            f.write(audio_bytes)

        print(f"音频已保存到: {output_file}")
    else:
        print("音频数据:")
        print(audio_data[:200] + "..." if len(audio_data) > 200 else audio_data)

    return audio_data


def list_system_voices():
    """列出可用的系统音色"""
    print("可用的系统音色:")
    print("-" * 60)

    lang_names = {
        "zh": "中文",
        "en": "英文",
        "ja": "日文",
        "ko": "韩文"
    }

    for lang, voices in SYSTEM_VOICES.items():
        print(f"{lang_names[lang]} ({lang}):")
        for voice in voices:
            print(f"  - {voice}")
        print()


def main():
    parser = argparse.ArgumentParser(description='阿里云语音合成')

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 合成子命令
    synth_parser = subparsers.add_parser('synthesize', help='合成语音')
    synth_parser.add_argument('text', help='待合成的文本')
    synth_parser.add_argument('--region', '-r', default='beijing',
                             choices=['beijing', 'singapore', 'us'],
                             help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    synth_parser.add_argument('--api-key', '-k', required=True,
                             help='阿里云 API Key')
    synth_parser.add_argument('--model', '-m', default='qwen3-tts-flash',
                             help='TTS模型，默认: qwen3-tts-flash (系统音色)')
    synth_parser.add_argument('--voice', '-v', default='Cherry',
                             help='音色名称（系统音色或复刻音色），默认: Cherry')
    synth_parser.add_argument('--language', '-l', default='Chinese',
                             choices=['Chinese', 'English', 'Japanese', 'Korean'],
                             help='文本语种，默认: Chinese')
    synth_parser.add_argument('--output', '-o',
                             help='输出音频文件路径（可选，需要绝对路径')
    synth_parser.add_argument('--stream', '-s', action='store_true',
                             help='流式输出（默认: 非流式）')

    # 列出色原子命令
    list_parser = subparsers.add_parser('list-voices', help='列出可用的系统音色')

    args = parser.parse_args()

    if args.command == 'synthesize':
        # 检查输出文件是否是绝对路径（如果提供了）
        if args.output and not os.path.isabs(args.output):
            print(f"错误：请提供绝对路径，而不是相对路径 {args.output}")
            sys.exit(1)

        synthesize_text(
            args.text,
            args.api_key,
            args.region,
            args.model,
            args.voice,
            args.language,
            args.output,
            args.stream
        )
    elif args.command == 'list-voices':
        list_system_voices()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
