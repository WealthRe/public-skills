#!/usr/bin/env python3
"""Run an OpenAI-compatible model smoke test without storing secrets."""

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
        print("Usage: model_smoke_test.py <demo-root>", file=sys.stderr)
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
        "reason": "OPENAI_API_KEY is not set",
    }

    if not api_key:
        write_report(root, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    source = (root / "sources" / "products" / "pinyuan-ai-appliance.md").read_text(
        encoding="utf-8"
    )
    prompt = (
        "Extract a tiny knowledge graph from the fake product source.\n"
        "Return valid JSON only. Do not use markdown fences. Do not add explanations.\n"
        "Use exactly this shape:\n"
        "{\"entities\":[{\"name\":\"品原AI一体机\",\"type\":\"product\"}],"
        "\"relations\":[{\"source\":\"品原AI一体机\",\"relation\":\"has_capability\",\"target\":\"模型推理服务\"}]}\n"
        "Allowed entity types: product, capability, component, scenario, boundary.\n"
        "Allowed relation values: has_capability, has_component, supports_scenario, constrained_by.\n"
        "Use short string values only. Do not include evidence text.\n"
        "Source text:\n\n"
        + source
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
            "content": "You extract small product knowledge graphs. Return strict JSON only.",
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
            raise ValueError("entities is not a list")
        if not isinstance(extracted.get("relations"), list):
            raise ValueError("relations is not a list")

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
