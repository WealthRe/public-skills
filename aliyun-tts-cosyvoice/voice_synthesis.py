#!/usr/bin/env python3
"""
阿里云 CosyVoice 语音合成脚本
支持使用系统音色或复刻音色进行语音合成

安全设计：
- 无硬编码 API Key
- 无硬编码音色名称
- 无硬编码输出路径
- 支持通过环境变量 DASHSCOPE_API_KEY 提供 API Key
"""

import os
import sys
import argparse
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer


# API 配置
REGIONS = {
    "beijing": {
        "websocket_url": "wss://dashscope.aliyuncs.com/api-ws/v1/inference",
        "http_url": "https://dashscope.aliyuncs.com/api/v1"
    },
    "singapore": {
        "websocket_url": "wss://dashscope-intl.aliyuncs.com/api-ws/v1/inference",
        "http_url": "https://dashscope-intl.aliyuncs.com/api/v1"
    },
    "us": {
        "websocket_url": "wss://dashscope-intl.aliyuncs.com/api-ws/v1/inference",
        "http_url": "https://dashscope-intl.aliyuncs.com/api/v1"
    }
}


def get_api_key(args):
    """获取 API Key，优先从参数获取，其次从环境变量获取"""
    if args.api_key:
        return args.api_key
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        print("错误：请提供 API Key，可以通过 --api-key 参数或 DASHSCOPE_API_KEY 环境变量提供")
        sys.exit(1)
    return api_key


def synthesize_text(text, api_key, region="beijing",
                    model="cosyvoice-v3-flash",
                    voice=None, output_file=None):
    """
    语音合成 - 非流式调用

    Args:
        text: 待合成的文本
        api_key: 阿里云 API Key
        region: 地域: beijing, singapore, 或 us
        model: TTS模型名称
        voice: 音色名称（系统音色或复刻音色）
        output_file: 输出音频文件路径（如果需要保存音频）
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    dashscope.api_key = api_key
    dashscope.base_websocket_api_url = config["websocket_url"]
    dashscope.base_http_api_url = config["http_url"]

    print(f"正在合成语音...")
    print(f"文本: {text}")
    print(f"模型: {model}")
    if voice:
        print(f"音色: {voice}")
    print(f"地域: {region}")
    print("-" * 60)

    try:
        # 重要：每次调用 call 前需要重新初始化 SpeechSynthesizer 实例
        synthesizer = SpeechSynthesizer(model=model, voice=voice)

        # 发送待合成文本，获取二进制音频
        audio_data = synthesizer.call(text)

        print(f"✓ 语音合成成功!")
        print(f"  Request ID: {synthesizer.get_last_request_id()}")
        print(f"  首包延迟: {synthesizer.get_first_package_delay()} 毫秒")
        print(f"  音频数据长度: {len(audio_data)} 字节")

        # 保存音频文件
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            print(f"✓ 音频已保存到: {output_file}")
        else:
            print("  提示：未指定输出文件，音频数据未保存")

        return audio_data

    except Exception as e:
        print(f"✗ 语音合成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='阿里云 CosyVoice 语音合成'
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 合成子命令
    synth_parser = subparsers.add_parser('synthesize', help='合成语音')
    synth_parser.add_argument('text', help='待合成的文本')
    synth_parser.add_argument('--region', '-r', default='beijing',
                             choices=['beijing', 'singapore', 'us'],
                             help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    synth_parser.add_argument('--api-key', '-k',
                             help='阿里云 API Key（也可通过 DASHSCOPE_API_KEY 环境变量提供）')
    synth_parser.add_argument('--model', '-m', default='cosyvoice-v3-flash',
                             help='TTS模型，默认: cosyvoice-v3-flash')
    synth_parser.add_argument('--voice', '-v',
                             help='音色名称（系统音色或复刻音色），可选')
    synth_parser.add_argument('--output', '-o',
                             help='输出音频文件路径（可选，需要绝对路径)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    api_key = get_api_key(args)

    if args.command == 'synthesize':
        # 检查输出文件是否是绝对路径（如果提供了）
        if args.output and not os.path.isabs(args.output):
            print(f"错误：请提供绝对路径，而不是相对路径 {args.output}")
            sys.exit(1)

        synthesize_text(
            args.text,
            api_key,
            args.region,
            args.model,
            args.voice,
            args.output
        )


if __name__ == "__main__":
    main()
