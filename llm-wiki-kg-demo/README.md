# LLM Wiki Knowledge Graph Demo

This directory validates the LLM Wiki plus lightweight knowledge graph workflow on fake AI-GTM product data.

## Scope

This demo proves four things:

- Markdown source files can be compiled into an Obsidian-style Wiki with `[[bidirectional links]]`.
- Wiki pages retain source paths, so claims remain traceable.
- Product facts can be represented as JSONL entities, relations, and evidence.
- A local validator can catch broken links, missing evidence, invalid JSONL, and dangling graph IDs.

## What This Does Not Prove

- It does not validate real company product facts.
- It does not require Neo4j, GraphRAG, or a vector database.
- It does not require committing Obsidian plugin settings.
- It does not store an API key in this repository.

## Directory Layout

```text
llm-wiki-kg-demo/
  sources/     Fake source Markdown files.
  wiki/        Obsidian-readable generated Wiki pages.
  graph/       JSONL knowledge graph files and schema.
  scripts/     Validation and model smoke-test scripts.
  reports/     Local validation reports safe to commit.
```

## Local Validation

Run:

```bash
python3 llm-wiki-kg-demo/scripts/validate_graph.py llm-wiki-kg-demo
```

Optional MiniMax-M3 smoke test:

```bash
export OPENAI_BASE_URL="https://api.minimaxi.com/v1"
export MODEL="MiniMax-M3"
export OPENAI_API_KEY="<set locally only>"
python3 llm-wiki-kg-demo/scripts/model_smoke_test.py llm-wiki-kg-demo
```

