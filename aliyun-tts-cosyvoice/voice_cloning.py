#!/usr/bin/env python3
"""
阿里云 CosyVoice 声音复刻脚本
支持创建、查询、列出、删除音色

安全设计：
- 无硬编码 API Key
- 无硬编码音频 URL
- 无硬编码音色名称
- 支持通过环境变量 DASHSCOPE_API_KEY 提供 API Key
"""

import os
import sys
import argparse
import time
import dashscope
from dashscope.audio.tts_v2 import VoiceEnrollmentService


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


def get_api_key(args):
    """获取 API Key，优先从参数获取，其次从环境变量获取"""
    if args.api_key:
        return args.api_key
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        print("错误：请提供 API Key，可以通过 --api-key 参数或 DASHSCOPE_API_KEY 环境变量提供")
        sys.exit(1)
    return api_key


def create_voice(audio_url, api_key, region="beijing",
                 target_model="cosyvoice-v3-flash",
                 prefix="myvoice", language_hints=None,
                 max_prompt_audio_length=None):
    """
    创建音色

    Args:
        audio_url: 公网可访问的音频文件URL
        api_key: 阿里云 API Key
        region: 地域: beijing, singapore, 或 us
        target_model: 驱动音色的语音合成模型
        prefix: 音色前缀（仅允许数字、大小写字母和下划线，不超过10个字符）
        language_hints: 语言提示列表
        max_prompt_audio_length: 音频预处理后用于声音复刻的参考音频最大时长（秒）
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    dashscope.api_key = api_key
    dashscope.base_http_api_url = config["api_url"]

    print(f"正在创建音色...")
    print(f"音频URL: {audio_url}")
    print(f"目标模型: {target_model}")
    print(f"前缀: {prefix}")
    if language_hints:
        print(f"语言提示: {language_hints}")
    print("-" * 60)

    try:
        service = VoiceEnrollmentService()

        create_kwargs = {
            "target_model": target_model,
            "prefix": prefix,
            "url": audio_url
        }

        if language_hints:
            create_kwargs["language_hints"] = language_hints
        if max_prompt_audio_length:
            create_kwargs["max_prompt_audio_length"] = max_prompt_audio_length

        voice_id = service.create_voice(**create_kwargs)

        print(f"✓ 音色创建请求已提交!")
        print(f"  Request ID: {service.get_last_request_id()}")
        print(f"  Voice ID: {voice_id}")
        print()
        print("=" * 60)
        print("重要：请保存好这个 Voice ID，后续语音合成时需要使用！")
        print("=" * 60)
        print()
        print("正在查询音色状态（需要等待部署完成）...")

        # 轮询查询状态
        max_attempts = 30
        poll_interval = 10

        for attempt in range(max_attempts):
            try:
                voice_info = service.query_voice(voice_id=voice_id)
                status = voice_info.get("status")
                print(f"  尝试 {attempt + 1}/{max_attempts}: 状态 = '{status}'")

                if status == "OK":
                    print()
                    print("✓ 音色已准备好，可以进行语音合成！")
                    print()
                    print("=" * 60)
                    print("音色创建成功！")
                    print("=" * 60)
                    print(f"Voice ID: {voice_id}")
                    print(f"状态: {status}")
                    for key, value in voice_info.items():
                        print(f"  {key}: {value}")
                    print("=" * 60)
                    print()
                    print("提示：可以使用以下命令进行语音合成：")
                    print(f"  aliyun-tts-cosyvoice synthesize \"你好，今天天气怎么样？\" \\\n    --api-key <your_api_key> \\\n    --model {target_model} \\\n    --voice {voice_id} \\\n    --output /absolute/path/to/output.wav")
                    break

                elif status == "UNDEPLOYED":
                    print()
                    print(f"✗ 音色处理失败，状态: {status}")
                    print("请检查音频质量或联系支持")
                    sys.exit(1)

                time.sleep(poll_interval)
            except Exception as e:
                print(f"  查询状态出错: {e}")
                time.sleep(poll_interval)
        else:
            print()
            print("轮询超时，音色在多次尝试后仍未就绪")
            sys.exit(1)

        return voice_id

    except Exception as e:
        print(f"✗ 创建音色失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def list_voices(api_key, region="beijing", prefix=None,
                page_index=0, page_size=10):
    """
    列出已创建的音色

    Args:
        api_key: 阿里云 API Key
        region: 地域: beijing, singapore, 或 us
        prefix: 音色前缀筛选（可选）
        page_index: 页索引
        page_size: 页大小
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    dashscope.api_key = api_key
    dashscope.base_http_api_url = config["api_url"]

    try:
        service = VoiceEnrollmentService()

        voices = service.list_voices(
            prefix=prefix,
            page_index=page_index,
            page_size=page_size
        )

        print(f"✓ Request ID: {service.get_last_request_id()}")
        print(f"✓ 找到 {len(voices)} 个音色:")
        print("-" * 80)

        for voice in voices:
            print(f"  Voice ID: {voice.get('voice_id')}")
            print(f"  状态: {voice.get('status')}")
            print(f"  创建时间: {voice.get('gmt_create')}")
            print(f"  修改时间: {voice.get('gmt_modified')}")
            print("-" * 80)

        return voices

    except Exception as e:
        print(f"✗ 查询音色列表失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def query_voice(voice_id, api_key, region="beijing"):
    """
    查询指定音色的详细信息

    Args:
        voice_id: 音色ID
        api_key: 阿里云 API Key
        region: 地域: beijing, singapore, 或 us
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    dashscope.api_key = api_key
    dashscope.base_http_api_url = config["api_url"]

    try:
        service = VoiceEnrollmentService()

        voice_info = service.query_voice(voice_id=voice_id)

        print(f"✓ Request ID: {service.get_last_request_id()}")
        print(f"✓ 音色详细信息:")
        print("-" * 80)
        for key, value in voice_info.items():
            print(f"  {key}: {value}")
        print("-" * 80)

        return voice_info

    except Exception as e:
        print(f"✗ 查询音色详情失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def delete_voice(voice_id, api_key, region="beijing"):
    """
    删除音色

    Args:
        voice_id: 音色ID
        api_key: 阿里云 API Key
        region: 地域: beijing, singapore, 或 us
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    dashscope.api_key = api_key
    dashscope.base_http_api_url = config["api_url"]

    try:
        service = VoiceEnrollmentService()

        service.delete_voice(voice_id=voice_id)

        print(f"✓ 音色删除请求已提交!")
        print(f"  Request ID: {service.get_last_request_id()}")

    except Exception as e:
        print(f"✗ 删除音色失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='阿里云 CosyVoice 声音复刻'
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 创建音色子命令
    create_parser = subparsers.add_parser('create', help='创建音色')
    create_parser.add_argument('audio_url', help='公网可访问的音频文件URL')
    create_parser.add_argument('--region', '-r', default='beijing',
                              choices=['beijing', 'singapore', 'us'],
                              help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    create_parser.add_argument('--api-key', '-k',
                              help='阿里云 API Key（也可通过 DASHSCOPE_API_KEY 环境变量提供）')
    create_parser.add_argument('--model', '-m', default='cosyvoice-v3-flash',
                              help='目标语音合成模型，默认: cosyvoice-v3-flash')
    create_parser.add_argument('--prefix', '-p', default='myvoice',
                              help='音色前缀（仅允许数字、大小写字母和下划线，不超过10个字符），默认: myvoice')
    create_parser.add_argument('--language', '-l',
                              help='语言提示: zh, en, fr, de, ja, ko, ru, pt, th, id, vi (仅适用于 cosyvoice-v3-flash/plus)')
    create_parser.add_argument('--max-length', type=float,
                              help='音频预处理后用于声音复刻的参考音频最大时长（秒），仅适用于 cosyvoice-v3-flash')

    # 列出色子命令
    list_parser = subparsers.add_parser('list', help='列出已创建的音色')
    list_parser.add_argument('--region', '-r', default='beijing',
                            choices=['beijing', 'singapore', 'us'],
                            help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    list_parser.add_argument('--api-key', '-k',
                            help='阿里云 API Key（也可通过 DASHSCOPE_API_KEY 环境变量提供）')
    list_parser.add_argument('--prefix', '-p',
                            help='音色前缀筛选（可选）')
    list_parser.add_argument('--page-index', type=int, default=0,
                            help='页索引，默认: 0')
    list_parser.add_argument('--page-size', type=int, default=10,
                            help='页大小，默认: 10')

    # 查询音色子命令
    query_parser = subparsers.add_parser('query', help='查询指定音色的详细信息')
    query_parser.add_argument('voice_id', help='音色ID')
    query_parser.add_argument('--region', '-r', default='beijing',
                              choices=['beijing', 'singapore', 'us'],
                              help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    query_parser.add_argument('--api-key', '-k',
                              help='阿里云 API Key（也可通过 DASHSCOPE_API_KEY 环境变量提供）')

    # 删除音色子命令
    delete_parser = subparsers.add_parser('delete', help='删除音色')
    delete_parser.add_argument('voice_id', help='音色ID')
    delete_parser.add_argument('--region', '-r', default='beijing',
                              choices=['beijing', 'singapore', 'us'],
                              help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    delete_parser.add_argument('--api-key', '-k',
                              help='阿里云 API Key（也可通过 DASHSCOPE_API_KEY 环境变量提供）')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    api_key = get_api_key(args)
    language_hints = [args.language] if hasattr(args, 'language') and args.language else None

    if args.command == 'create':
        create_voice(
            args.audio_url,
            api_key,
            args.region,
            args.model,
            args.prefix,
            language_hints,
            args.max_length if hasattr(args, 'max_length') else None
        )
    elif args.command == 'list':
        list_voices(
            api_key,
            args.region,
            args.prefix,
            args.page_index,
            args.page_size
        )
    elif args.command == 'query':
        query_voice(
            args.voice_id,
            api_key,
            args.region
        )
    elif args.command == 'delete':
        delete_voice(
            args.voice_id,
            api_key,
            args.region
        )


if __name__ == "__main__":
    main()
