# Karpathy LLM Wiki 增删查改验证报告

验证日期：2026-06-27

验证仓库：`WealthRe/public-skills` 的本地验证分支 `verify/llm-wiki-kg-demo-20260627`

验证目录：`llm-wiki-kg-demo`

## 结论

Karpathy LLM Wiki + Obsidian + MiniMax 国内 Token Plan 这条路径可以走通，适合做“Markdown 知识库自动摄入、双向链接生成、基于 Wiki 的自然语言查询”。

本轮已实测通过：

- Obsidian 插件安装、启用、连接 MiniMax-M3。
- 新增 Markdown 源资料后，插件可生成 source summary、entity 页面、concept 页面和双向链接。
- 修改源资料后，重新摄入能把新增验收指标写回 source summary、实体页和概念页。
- Karpathy 查询面板能基于生成的 Wiki 回答问题，并返回 Obsidian 内部引用链接。
- 源文件临时移走后，已生成 Wiki 页面不会自动级联删除；删除流程应采用“软删除/废弃标记 + Lint/人工整理”。

不建议直接把它当成完全自动化的企业知识图谱系统。它更适合作为 Obsidian 内的知识整理与查询层；后续知识图谱可以把它生成的 Wiki 链接、来源字段和实体页作为输入，再导出到 JSONL、Neo4j 或 GraphRAG。

## 使用组件

- Obsidian：1.12.7
- Karpathy LLM Wiki：1.22.4
- 模型接口：MiniMax 国内 Token Plan OpenAI-compatible endpoint
- Base URL：`https://api.minimaxi.com/v1`
- Model：`MiniMax-M3`
- 官方配置参考：<https://platform.minimaxi.com/docs/token-plan/other-tools>
- 插件仓库参考：<https://github.com/green-dalii/obsidian-llm-wiki>

说明：API Key 只保存在本机 Obsidian 忽略目录和本机环境中，不写入 Git 仓库。`.obsidian/` 已由 `llm-wiki-kg-demo/.gitignore` 忽略。

## 验证数据

新增源文件：

`sources/daily/2026-06-27-retail-edge-poc.md`

模拟内容是一个假项目：华东零售门店边缘推理 POC。它包含背景、方案、报价边界，以及后续补充的验收指标。

关键事实：

- POC 面向 80 家连锁门店。
- 首期只验证 10 家样板门店。
- 采用“品原 AI 一体机 + AI 原生推理平台”。
- 报价边界不包含摄像头改造、弱电施工、客户自有 POS 改造。
- 修改后新增三项验收指标：平均推理时延、离线缓存保留时长、告警误报率。
- 离线缓存保留时长不少于 24 小时。
- 不承诺替换客户已有视频管理平台。

## 增：新增源资料并摄入

操作：

- 在 `sources/daily/` 下创建一篇新的 Markdown 源资料。
- 在 Obsidian 中打开该文件。
- 点击 Karpathy LLM Wiki 左侧按钮“摄入当前文件”。

第一次摄入结果：

- 耗时：3 分 38 秒。
- 创建页面：5 页。
- 更新页面：1 页。
- 新建页面包括：
  - `wiki/sources/2026-06-27-retail-edge-poc_0f3c2f.md`
  - `wiki/entities/华东零售门店边缘推理-POC.md`
  - `wiki/entities/品原-AI-一体机.md`
  - `wiki/entities/AI-原生推理平台.md`
  - `wiki/concepts/报价边界.md`

验证结果：通过。

实际效果：

- 原始源文件在 Obsidian 中出现反向链接。
- 生成的 source summary 保留了原始 source 路径。
- 生成的实体页、概念页之间建立了 `[[双向链接]]`。

## 改：修改源资料并重新摄入

操作：

- 在同一源文件追加“2026-06-27 变更记录”。
- 新增客户验收要求：平均推理时延、离线缓存保留时长、告警误报率。
- 再次点击“摄入当前文件”。

第二次摄入结果：

- 耗时：7 分 0 秒。
- 创建页面：7 页。
- 更新页面：6 页。
- 新增或补齐的概念页包括：
  - `wiki/concepts/边缘推理.md`
  - `wiki/concepts/模型推理.md`
- 变更内容被写入：
  - `wiki/sources/2026-06-27-retail-edge-poc_0f3c2f.md`
  - `wiki/entities/华东零售门店边缘推理-POC.md`
  - `wiki/concepts/边缘推理.md`
  - `wiki/concepts/模型推理.md`

验证结果：通过。

命中证据：

- `平均推理时延`
- `离线缓存保留时长（不少于 24 小时）`
- `告警误报率`
- `不替换客户已有的视频管理平台`

注意：重摄入不是只更新一个摘要页，它会重跑相关实体/概念页，因此耗时会变长，也可能改写已有生成页。

## 查：使用 Karpathy 查询 Wiki

操作：

- 打开 Karpathy 右侧“Query Wiki - 对话式查询”面板。
- 输入问题：`华东零售门店边缘推理 POC 的验收指标和报价边界是什么？`
- 点击发送。

查询结果：

- 成功返回答案。
- 答案正确列出三项验收指标：
  - 平均推理时延。
  - 离线缓存保留时长不少于 24 小时。
  - 告警误报率。
- 答案正确列出报价边界：
  - 不含摄像头改造。
  - 不含弱电施工。
  - 不含客户自有 POS 系统改造。
  - 不替换客户已有视频管理平台。
  - 首期只验证 10 家样板门店，不承诺全量 80 家门店上线排期。
- 答案给出 Obsidian 内部引用链接，包括：
  - `wiki/entities/华东零售门店边缘推理-POC`
  - `wiki/sources/2026-06-27-retail-edge-poc_0f3c2f`
  - `wiki/concepts/报价边界`

验证结果：通过。

## 删：源文件删除与废弃规则

操作：

- 临时移走源文件 `sources/daily/2026-06-27-retail-edge-poc.md`。
- 检查已生成 Wiki 页面是否仍存在。
- 立即恢复源文件。

测试结果：

```text
source_exists_after_move=no
wiki_source_page_exists_after_move=yes
wiki_entity_page_exists_after_move=yes
source_restored=yes
```

验证结果：部分通过，但结论不是“自动删除可用”，而是“不能依赖自动级联删除”。

删除规则：

- 不把物理删除作为日常知识库删除主流程。
- 源资料过期时，先在源文件或生成页标记 `deprecated`、`废弃`、`替代来源`、`废弃原因`。
- 确认没有业务引用后，再手工删除对应 Wiki 页。
- 删除后必须运行 Lint 或本地校验脚本，确认没有死链。
- 对重要业务知识，保留废弃记录比直接删除更可靠。

## 本地校验

运行命令：

```bash
python3 llm-wiki-kg-demo/scripts/validate_graph.py llm-wiki-kg-demo
```

结果：

```json
{
  "status": "pass",
  "root": "llm-wiki-kg-demo",
  "entities": 9,
  "relations": 10,
  "evidence": 9,
  "wiki_pages": 14,
  "wiki_links": 143
}
```

本轮同步升级了 `validate_graph.py`，让它兼容 Karpathy 生成的 Obsidian 路径型链接，例如：

- `[[entities/页面名]]`
- `[[entities/页面名.md]]`
- `[[sources/daily/原始文件]]`

同时跳过 `wiki/schema/` 中的模板示例链接，避免把 `[[entities/...]]` 这类占位符误判为死链。

## 模型接口校验

运行 `model_smoke_test.py` 后结果：

```json
{
  "status": "pass",
  "api_status": "pass",
  "strict_json_status": "pass",
  "base_url": "https://api.minimaxi.com/v1",
  "model": "MiniMax-M3",
  "entity_count": 11,
  "relation_count": 10
}
```

结论：

- MiniMax 国内 Token Plan endpoint 可用。
- `MiniMax-M3` 可用于 OpenAI-compatible chat/completions。
- 模型能按要求返回结构化 JSON。

## 安全校验

已检查：

- `.obsidian/` 被 Git ignore。
- `llm-wiki-kg-demo/.obsidian/plugins/karpathywiki/data.json` 不会提交。
- 仓库扫描未发现真实 MiniMax API Key。
- 扫描结果只包含代码变量、模板占位符和 README 中的本机环境变量说明。

结论：通过。

## 存在价值

这套东西的价值不是“把 Obsidian 做漂亮”，而是把零散 Markdown 资料变成可追溯、可查询、可逐步图谱化的知识底座。

适合的场景：

- 每天有会议纪要、客户需求、产品说明、方案边界等 Markdown 文档。
- 人不想手工维护大量双链。
- 需要快速问：“某项目验收指标是什么？”“这个报价边界在哪些案例出现过？”“这个产品能力和哪些场景有关？”
- 后续想把知识转成图谱，但现在还不想直接上 Neo4j、向量库、GraphRAG。

不适合的场景：

- 要求 100% 可重复、可审计、结构严格的知识抽取。
- 希望源文件删除后自动级联清理所有派生知识。
- 希望 LLM 自动维护企业级主数据、权限、版本和审批。
- 希望完全不经过人工 review 就把生成知识作为正式事实库。

## 与自研 Wiki/JSONL Demo 的区别

Karpathy LLM Wiki 更强的地方：

- 直接接入 Obsidian。
- 自动生成实体页、概念页、source summary。
- 自动建立双向链接。
- 自带查询面板。
- 自带 Lint/维护能力。
- 更适合日常个人或小团队知识库使用。

自研 Wiki/JSONL Demo 更强的地方：

- 输出结构可控。
- CI 校验更稳定。
- JSONL 图谱更适合后续导入 Neo4j、GraphRAG 或数据管道。
- 不容易被 LLM 重摄入时改写既有页面。
- 更适合作为工程化知识图谱的中间层。

推荐组合方式：

- Obsidian + Karpathy：负责日常摄入、双链、阅读和查询。
- JSONL/脚本：负责稳定校验、导出、图谱化和 CI。
- 后续知识图谱：从 Wiki 的 entity/concept/source 页面和 JSONL 关系中抽取，不直接依赖 Obsidian UI。

## 推荐日常使用路径

1. 写源资料

把会议纪要、客户需求、产品说明、方案边界放到 `sources/`。建议按类型分目录：

- `sources/daily/`
- `sources/cases/`
- `sources/products/`
- `sources/policies/`

2. 摄入当前文件

在 Obsidian 打开源文件，点击“摄入当前文件”。生成后先看：

- source summary 是否准确。
- 新建实体是否重复。
- 报价边界、验收指标等是否被抽到正确页面。
- 原始 source 是否保留。

3. 查询验证

用 Query Wiki 问一个能检验事实的问题，例如：

- `这个 POC 的验收指标是什么？`
- `报价边界不包含哪些内容？`
- `品原 AI 一体机在哪些案例中出现过？`
- `边缘推理和模型推理在这些资料里是什么关系？`

4. 修改后重摄入

源资料变更后，直接改源文件，再重新摄入。不要直接把所有事实只改在生成页里，否则后续追溯会断。

5. 废弃而不是直接删除

资料过期时，优先加废弃说明：

```markdown
## 废弃记录

- 状态：已废弃
- 废弃日期：2026-06-27
- 废弃原因：客户验收口径已被新版方案替代
- 替代来源：[[sources/daily/新版文件]]
```

确认没有引用后，再手工删除生成页并运行校验。

6. 定期治理

建议每周做一次：

- 跑 Karpathy Lint。
- 跑 `validate_graph.py`。
- 检查重复实体。
- 检查过时 source。
- 把稳定事实导出到 JSONL 图谱。

## 规则要求

必须做：

- API Key 只放本机环境或 Obsidian 本地配置。
- `.obsidian/` 不提交。
- 源资料必须保留在 `sources/`，生成页必须能追溯 source。
- 重要业务事实修改必须先改 source，再重摄入。
- 删除必须先软删除，后清理派生页。
- 每次批量摄入后跑本地校验。

不做：

- 不把生成页直接当最终事实，不经 review 就对外使用。
- 不把 API Key 写入 README、报告、脚本默认值或 Git 历史。
- 不把 GitLab/GitHub 当唯一知识源；代码仓库只保存可提交资料，Obsidian 本地配置仍留本机。
- 不指望 Karpathy 自动解决实体重复、主数据归一、权限隔离。
- 不把“查询回答正确一次”当成知识图谱已经建成。

## 已发现问题

1. 重摄入较慢

第二次小文件重摄入耗时 7 分钟。原因是插件会重跑相关实体、概念和摘要页。生产使用时需要控制并发、批量节奏和成本。

2. 实体类型可能重复

仓库中原本已有：

- `wiki/products/品原AI一体机.md`
- `wiki/products/AI原生推理平台.md`

Karpathy 又新建：

- `wiki/entities/品原-AI-一体机.md`
- `wiki/entities/AI-原生推理平台.md`

这不是死链，但会造成“产品页”和“实体页”重复表达。后续要明确命名和类型规则。

3. 删除不自动级联

源文件移走后，生成的 source summary 和实体页仍存在。删除要作为治理流程处理，不能当作插件自动能力。

4. 生成页可能改写旧内容

Karpathy 的更新策略会合并/补写已有生成页。对于人工审核过的正式页面，建议加 reviewed 标记或放到受控目录，避免被随意重摄入改写。

## 验收标准

| 验收项 | 标准 | 结果 |
| --- | --- | --- |
| Obsidian 可打开 vault | 能打开 `llm-wiki-kg-demo` | 通过 |
| Karpathy 插件可用 | 插件启用，Test Connection 通过 | 通过 |
| MiniMax 接口可用 | `MiniMax-M3` chat/completions 成功 | 通过 |
| 新增资料可摄入 | 生成 source/entity/concept 页面 | 通过 |
| 修改资料可重摄入 | 新增验收指标进入生成页 | 通过 |
| Wiki 查询可用 | 查询能回答验收指标和报价边界 | 通过 |
| 删除行为明确 | 已验证不会自动级联删除，形成软删除规则 | 通过 |
| 双链校验 | `validate_graph.py` 通过 | 通过 |
| 敏感信息 | 仓库未发现真实 API Key | 通过 |

## 最终判断

验证阶段可以进入下一步：用 Karpathy LLM Wiki 做一段“模拟日常使用”的小规模试运行。

建议下一阶段目标：

- 连续放入 10 到 20 篇假资料或脱敏资料。
- 覆盖产品、客户、案例、报价边界、验收指标、风险问题。
- 每天执行新增、修改、查询、废弃。
- 每周导出一次 JSONL 图谱。
- 重点观察重复实体、错误链接、查询质量、重摄入成本和人工修正成本。

如果下一阶段也稳定，再考虑把 Wiki 链接关系导出成正式知识图谱。
