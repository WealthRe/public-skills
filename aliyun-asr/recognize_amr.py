#!/usr/bin/env python3
"""
阿里云千问3-ASR-Flash 语音识别脚本
支持北京和新加坡地域
"""

import os
import sys
import argparse

try:
    import dashscope
except ImportError:
    print("错误：请先安装 dashscope SDK")
    print("  pip install dashscope")
    sys.exit(1)

# API 配置 - 只保留 URL 和模型名称，API Key 由用户提供
REGIONS = {
    "beijing": {
        "api_url": "https://dashscope.aliyuncs.com/api/v1",
        "model": "qwen3-asr-flash"
    },
    "singapore": {
        "api_url": "https://dashscope-intl.aliyuncs.com/api/v1",
        "model": "qwen3-asr-flash"
    },
    "us": {
        "api_url": "https://dashscope-intl.aliyuncs.com/api/v1",
        "model": "qwen3-asr-flash"
    }
}


def recognize_audio(audio_path, region, api_key):
    """识别音频文件"""
    config = REGIONS.get(region)
    if not config:
        print(f"错误：未知地域 {region}")
        sys.exit(1)

    # 检查文件是否存在
    if not os.path.exists(audio_path):
        print(f"错误：文件不存在 {audio_path}")
        sys.exit(1)

    # 检查是否是绝对路径
    if not os.path.isabs(audio_path):
        print(f"错误：请提供绝对路径，而不是相对路径 {audio_path}")
        sys.exit(1)

    # 配置 dashscope
    dashscope.base_http_api_url = config["api_url"]

    # 构建 file:// URL
    audio_url = f"file://{audio_path}"

    messages = [
        {"role": "system", "content": [{"text": ""}]},
        {"role": "user", "content": [{"audio": audio_url}]}
    ]

    try:
        response = dashscope.MultiModalConversation.call(
            api_key=api_key,
            model=config["model"],
            messages=messages,
            result_format="message",
            asr_options={
                "enable_itn": False
            }
        )

        # 提取识别结果
        if isinstance(response, dict):
            output = response.get('output', {})
            choices = output.get('choices', [])
            if choices:
                message = choices[0].get('message', {})
                content = message.get('content', [])
                if content:
                    text = content[0].get('text', '')
                    # 只输出识别结果
                    print(text)
                    return text

        print("错误：无法提取识别结果")
        return None

    except Exception as e:
        print(f"识别失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='阿里云 ASR 语音识别')
    parser.add_argument('audio_file', help='音频文件绝对路径')
    parser.add_argument('--region', '-r', required=True,
                        choices=['beijing', 'singapore', 'us'],
                        help='地域: beijing (北京), singapore (新加坡), 或 us (美国)')
    parser.add_argument('--api-key', '-k', required=True,
                        help='阿里云 API Key')

    args = parser.parse_args()

    recognize_audio(args.audio_file, args.region, args.api_key)


if __name__ == "__main__":
    main()
