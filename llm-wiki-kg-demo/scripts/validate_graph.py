#!/usr/bin/env python3
"""校验 demo 的 LLM Wiki 和 JSONL 知识图谱。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ALLOWED_RELATIONS = {
    "has_capability",
    "has_component",
    "supports_scenario",
    "used_in_case",
    "documented_by",
    "constrained_by",
    "depends_on",
    "documents_capability",
}


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path}:{line_no} 不是合法 JSON: {exc}") from exc
    return rows


def validate_required_files(root: Path) -> None:
    required = [
        root / "README.md",
        root / "sources" / "INDEX.md",
        root / "wiki" / "index.md",
        root / "wiki" / "log.md",
        root / "graph" / "schema.md",
        root / "graph" / "entities.jsonl",
        root / "graph" / "relations.jsonl",
        root / "graph" / "evidence.jsonl",
        root / "graph" / "validation.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise AssertionError("缺少必要文件: " + ", ".join(missing))


def validate_graph(root: Path) -> dict:
    entities = load_jsonl(root / "graph" / "entities.jsonl")
    relations = load_jsonl(root / "graph" / "relations.jsonl")
    evidence = load_jsonl(root / "graph" / "evidence.jsonl")

    entity_ids = {row["id"] for row in entities}
    evidence_ids = {row["id"] for row in evidence}

    if len(entity_ids) != len(entities):
        raise AssertionError("发现重复实体 ID")
    if len(evidence_ids) != len(evidence):
        raise AssertionError("发现重复证据 ID")

    for row in entities:
        for field in ("id", "name", "type", "source_paths"):
            if field not in row:
                raise AssertionError(f"实体缺少字段 {field}: {row}")
        for source_path in row["source_paths"]:
            if not (root.parent / source_path).exists():
                raise AssertionError(f"实体来源路径不存在: {source_path}")

    for row in evidence:
        if not (root.parent / row["path"]).exists():
            raise AssertionError(f"证据路径不存在: {row['path']}")

    for row in relations:
        for field in ("source_id", "relation", "target_id", "evidence_id"):
            if field not in row:
                raise AssertionError(f"关系缺少字段 {field}: {row}")
        if row["source_id"] not in entity_ids:
            raise AssertionError(f"关系源实体不存在: {row['source_id']}")
        if row["target_id"] not in entity_ids:
            raise AssertionError(f"关系目标实体不存在: {row['target_id']}")
        if row["evidence_id"] not in evidence_ids:
            raise AssertionError(f"关系证据不存在: {row['evidence_id']}")
        if row["relation"] not in ALLOWED_RELATIONS:
            raise AssertionError(f"关系类型不在允许列表中: {row['relation']}")

    return {
        "entities": len(entities),
        "relations": len(relations),
        "evidence": len(evidence),
    }


def validate_wiki_links(root: Path) -> dict:
    wiki_root = root / "wiki"
    pages = {path.stem for path in wiki_root.rglob("*.md")}
    link_pattern = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
    checked = 0
    missing: list[str] = []

    for path in wiki_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in link_pattern.finditer(text):
            checked += 1
            target = match.group(1).strip()
            if target not in pages:
                missing.append(f"{path.relative_to(root)} -> {target}")

    if missing:
        raise AssertionError("发现 Wiki 死链: " + "; ".join(missing))

    return {"wiki_pages": len(pages), "wiki_links": checked}


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: validate_graph.py <demo-root>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    validate_required_files(root)
    graph_summary = validate_graph(root)
    wiki_summary = validate_wiki_links(root)

    try:
        display_root = str(root.relative_to(Path.cwd().resolve()))
    except ValueError:
        display_root = root.name

    summary = {
        "status": "pass",
        "root": display_root,
        **graph_summary,
        **wiki_summary,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
