# 图谱 Schema

## 实体类型

| 类型 | 含义 |
| --- | --- |
| `product` | 产品或平台 |
| `capability` | 产品能力 |
| `component` | 产品组件 |
| `scenario` | 使用场景 |
| `case` | 项目、POC 或交付案例 |
| `boundary` | 业务边界或非最终结论边界 |

## 关系类型

| 关系 | 含义 |
| --- | --- |
| `has_capability` | 产品具备某项能力 |
| `has_component` | 产品包含某个组件 |
| `supports_scenario` | 实体支持某个使用场景 |
| `used_in_case` | 产品或能力出现在某个案例中 |
| `documented_by` | 实体由来源证据说明 |
| `documents_capability` | 案例或文档证明某项能力 |
| `constrained_by` | 实体受某个边界约束 |
| `depends_on` | 实体依赖另一个实体 |

## 证据规则

每条关系都必须包含 `evidence_id`。每条证据记录都必须指向一个真实存在的来源文件。
