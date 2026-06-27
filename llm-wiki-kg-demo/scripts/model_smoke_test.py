#!/usr/bin/env python3
"""在不保存密钥的前提下运行 OpenAI-compatible 模型 smoke test。"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def extract_json(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end >= start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


def write_report(root: Path, report: dict) -> None:
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "model-smoke-test.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: model_smoke_test.py <demo-root>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.minimaxi.com/v1").rstrip("/")
    model = os.environ.get("MODEL", "MiniMax-M3")
    api_key = os.environ.get("OPENAI_API_KEY")

    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    report = {
        "status": "skipped",
        "started_at": started_at,
        "base_url": base_url,
        "model": model,
        "reason": "未设置 OPENAI_API_KEY",
    }

    if not api_key:
        write_report(root, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    source = (root / "sources" / "products" / "pinyuan-ai-appliance.md").read_text(
        encoding="utf-8"
    )
    prompt = (
        "请从下面的假产品资料中抽取一个很小的知识图谱。\n"
        "只返回合法 JSON，不要使用 markdown 代码块，不要添加解释。\n"
        "严格使用这个结构:\n"
        "{\"entities\":[{\"name\":\"品原AI一体机\",\"type\":\"product\"}],"
        "\"relations\":[{\"source\":\"品原AI一体机\",\"relation\":\"has_capability\",\"target\":\"模型推理服务\"}]}\n"
        "允许的实体类型: product, capability, component, scenario, boundary。\n"
        "允许的关系类型: has_capability, has_component, supports_scenario, constrained_by。\n"
        "只使用短字符串值，不要包含证据原文。\n"
        "源资料:\n\n"
        + source
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
            "content": "你负责抽取小型产品知识图谱。只返回严格 JSON。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 800,
    }

    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
        data = json.loads(response_body)
        content = data["choices"][0]["message"]["content"]
        extracted = extract_json(content)
        if not isinstance(extracted.get("entities"), list):
            raise ValueError("entities 不是列表")
        if not isinstance(extracted.get("relations"), list):
            raise ValueError("relations 不是列表")

        report = {
            "status": "pass",
            "api_status": "pass",
            "strict_json_status": "pass",
            "started_at": started_at,
            "base_url": base_url,
            "model": model,
            "entity_count": len(extracted["entities"]),
            "relation_count": len(extracted["relations"]),
            "sample_entity_names": [
                row.get("name") for row in extracted["entities"][:5] if isinstance(row, dict)
            ],
        }
        write_report(root, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "status": "fail",
            "api_status": "unknown",
            "strict_json_status": "fail",
            "started_at": started_at,
            "base_url": base_url,
            "model": model,
            "reason": str(exc),
        }
        if "response_body" in locals():
            report["api_status"] = "pass"
        write_report(root, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
