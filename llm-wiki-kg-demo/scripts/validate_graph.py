#!/usr/bin/env python3
"""Validate the demo LLM Wiki and JSONL knowledge graph."""

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
                raise AssertionError(f"{path}:{line_no} invalid JSON: {exc}") from exc
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
        raise AssertionError("Missing required files: " + ", ".join(missing))


def validate_graph(root: Path) -> dict:
    entities = load_jsonl(root / "graph" / "entities.jsonl")
    relations = load_jsonl(root / "graph" / "relations.jsonl")
    evidence = load_jsonl(root / "graph" / "evidence.jsonl")

    entity_ids = {row["id"] for row in entities}
    evidence_ids = {row["id"] for row in evidence}

    if len(entity_ids) != len(entities):
        raise AssertionError("Duplicate entity IDs found")
    if len(evidence_ids) != len(evidence):
        raise AssertionError("Duplicate evidence IDs found")

    for row in entities:
        for field in ("id", "name", "type", "source_paths"):
            if field not in row:
                raise AssertionError(f"Entity missing {field}: {row}")
        for source_path in row["source_paths"]:
            if not (root.parent / source_path).exists():
                raise AssertionError(f"Entity source path does not exist: {source_path}")

    for row in evidence:
        if not (root.parent / row["path"]).exists():
            raise AssertionError(f"Evidence path does not exist: {row['path']}")

    for row in relations:
        for field in ("source_id", "relation", "target_id", "evidence_id"):
            if field not in row:
                raise AssertionError(f"Relation missing {field}: {row}")
        if row["source_id"] not in entity_ids:
            raise AssertionError(f"Relation source not found: {row['source_id']}")
        if row["target_id"] not in entity_ids:
            raise AssertionError(f"Relation target not found: {row['target_id']}")
        if row["evidence_id"] not in evidence_ids:
            raise AssertionError(f"Relation evidence not found: {row['evidence_id']}")
        if row["relation"] not in ALLOWED_RELATIONS:
            raise AssertionError(f"Relation type not allowed: {row['relation']}")

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
        raise AssertionError("Broken wiki links: " + "; ".join(missing))

    return {"wiki_pages": len(pages), "wiki_links": checked}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_graph.py <demo-root>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    validate_required_files(root)
    graph_summary = validate_graph(root)
    wiki_summary = validate_wiki_links(root)

    summary = {
        "status": "pass",
        "root": str(root),
        **graph_summary,
        **wiki_summary,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

