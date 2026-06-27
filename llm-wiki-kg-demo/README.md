# LLM Wiki 知识图谱验证 Demo

这个目录用于用假数据验证“LLM Wiki + 轻量知识图谱”的流程是否走得通。

## 验证范围

这个 demo 验证四件事：

- Markdown 源文件可以整理成 Obsidian 风格的 Wiki，并使用 `[[双向链接]]`。
- Wiki 页面保留来源路径，便于追溯每条结论。
- 产品事实可以拆成 JSONL 格式的实体、关系和证据。
- 本地校验脚本可以检查死链、缺失证据、非法 JSONL 和悬空图谱 ID。

## 不验证什么

- 不验证真实公司产品事实。
- 不依赖 Neo4j、GraphRAG 或向量数据库。
- 不要求提交 Obsidian 插件配置。
- 不在仓库中保存 API key。

## 目录结构

```text
llm-wiki-kg-demo/
  sources/     假源资料 Markdown 文件。
  wiki/        Obsidian 可读的生成 Wiki 页面。
  graph/       JSONL 知识图谱文件和 schema。
  scripts/     校验脚本和模型 smoke test 脚本。
  reports/     可提交的本地校验报告。
```

## 本地校验

Run:

```bash
python3 llm-wiki-kg-demo/scripts/validate_graph.py llm-wiki-kg-demo
```

可选的 MiniMax-M3 smoke test：

```bash
export OPENAI_BASE_URL="https://api.minimaxi.com/v1"
export MODEL="MiniMax-M3"
export OPENAI_API_KEY="<只在本机设置>"
python3 llm-wiki-kg-demo/scripts/model_smoke_test.py llm-wiki-kg-demo
```
