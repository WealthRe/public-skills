#!/usr/bin/env python3
"""
阿里云千问声音复刻脚本
使用 qwen-voice-enrollment 模型创建专属音色
"""

import os
import sys
import argparse
import base64
import pathlib
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


def get_mime_type(file_path):
    """根据文件扩展名获取MIME类型"""
    ext = pathlib.Path(file_path).suffix.lower()
    mime_types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".aac": "audio/aac",
        ".ogg": "audio/ogg"
    }
    return mime_types.get(ext, "audio/mpeg")


def create_voice(file_path, api_key, region="beijing",
                 target_model="qwen3-tts-vc-2026-01-22",
                 preferred_name="custom_voice"):
    """
    创建声音复刻音色

    Args:
        file_path: 音频文件路径（绝对路径）
        api_key: 阿里云 API Key
        region: 地域: beijing 或 singapore
        target_model: 目标TTS模型
        preferred_name: 音色名称

    Returns:
        生成的音色名称
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 {file_path}")
        sys.exit(1)

    # 检查是否是绝对路径
    if not os.path.isabs(file_path):
        print(f"错误：请提供绝对路径，而不是相对路径 {file_path}")
        sys.exit(1)

    # 读取并编码音频文件
    file_obj = pathlib.Path(file_path)
    base64_str = base64.b64encode(file_obj.read_bytes()).decode()
    audio_mime_type = get_mime_type(file_path)
    data_uri = f"data:{audio_mime_type};base64,{base64_str}"

    # 构建API URL
    base_url = config["api_url"]
    url = f"{base_url}/services/audio/tts/customization"

    payload = {
        "model": "qwen-voice-enrollment",
        "input": {
            "action": "create",
            "target_model": target_model,
            "preferred_name": preferred_name,
            "audio": {"data": data_uri}
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)

        if resp.status_code == 200:
            result = resp.json()
            voice = result["output"]["voice"]
            print(f"声音复刻成功！")
            print(f"音色名称: {voice}")
            print(f"目标模型: {target_model}")
            return voice
        else:
            print(f"请求失败: {resp.status_code}")
            print(f"响应内容: {resp.text}")
            sys.exit(1)

    except Exception as e:
        print(f"声音复刻失败: {e}")
        sys.exit(1)


def list_voices(api_key, region="beijing", target_model=None):
    """
    查询已创建的音色列表

    Args:
        api_key: 阿里云 API Key
        region: 地域: beijing 或 singapore
        target_model: 可选，筛选特定模型的音色
    """
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    # 构建API URL
    base_url = config["api_url"]
    url = f"{base_url}/services/audio/tts/customization"

    payload = {
        "model": "qwen-voice-enrollment",
        "input": {
            "action": "list"
        }
    }

    if target_model:
        payload["input"]["target_model"] = target_model

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)

        if resp.status_code == 200:
            result = resp.json()
            voices = result["output"].get("voices", [])

            if not voices:
                print("暂无已创建的音色")
                return

            print(f"已创建的音色列表 ({len(voices)} 个):")
            print("-" * 60)
            for voice in voices:
                print(f"音色名称: {voice.get('voice')}")
                print(f"目标模型: {voice.get('target_model')}")
                print(f"创建时间: {voice.get('create_time')}")
                print("-" * 60)

            return voices
        else:
            print(f"请求失败: {resp.status_code}")
            print(f"响应内容: {resp.text}")
            sys.exit(1)

    except Exception as e:
        print(f"查询音色列表失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='阿里云声音复刻')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 创建音色子命令
    create_parser = subparsers.add_parser('create', help='创建声音复刻音色')
    create_parser.add_argument('audio_file', help='音频文件绝对路径 (支持 WAV/MP3/M4A 等格式)')
    create_parser.add_argument('--region', '-r', default='beijing',
                             choices=['beijing', 'singapore', 'us'],
                             help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    create_parser.add_argument('--api-key', '-k', required=True,
                             help='阿里云 API Key')
    create_parser.add_argument('--model', '-m', default='qwen3-tts-vc-2026-01-22',
                             help='目标TTS模型，默认: qwen3-tts-vc-2026-01-22 (非流式推荐)')
    create_parser.add_argument('--name', '-n', default='custom_voice',
                             help='音色名称，默认: custom_voice')

    # 列出色原子命令
    list_parser = subparsers.add_parser('list', help='查询已创建的音色列表')
    list_parser.add_argument('--region', '-r', default='beijing',
                            choices=['beijing', 'singapore', 'us'],
                            help='地域: beijing (北京), singapore (新加坡), 或 us (美国)，默认: beijing')
    list_parser.add_argument('--api-key', '-k', required=True,
                            help='阿里云 API Key')
    list_parser.add_argument('--model', '-m',
                            help='可选，筛选特定模型的音色')

    args = parser.parse_args()

    if args.command == 'create':
        create_voice(args.audio_file, args.api_key, args.region, args.model, args.name)
    elif args.command == 'list':
        list_voices(args.api_key, args.region, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
