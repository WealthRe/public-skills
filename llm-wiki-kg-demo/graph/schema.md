# Graph Schema

## Entity Types

| Type | Meaning |
| --- | --- |
| `product` | Product or platform |
| `capability` | Product capability |
| `component` | Product component |
| `scenario` | Usage scenario |
| `case` | Project, POC, or delivery case |
| `boundary` | Business constraint or non-final boundary |

## Relation Types

| Relation | Meaning |
| --- | --- |
| `has_capability` | Product has a capability |
| `has_component` | Product has a component |
| `supports_scenario` | Entity supports a usage scenario |
| `used_in_case` | Product or capability appears in a case |
| `documented_by` | Entity is documented by source evidence |
| `documents_capability` | Case or document confirms a capability |
| `constrained_by` | Entity is limited by a boundary |
| `depends_on` | Entity depends on another entity |

## Evidence Rule

Every relation must include `evidence_id`. Every evidence record must point to an existing source file.
