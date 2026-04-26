# OMK 技术文档索引

本目录收录 OMK（Oh-My-Kimi）面向开发者与维护者的中文技术设计文档，涵盖需求定义、架构决策、系统设计与功能规格，用于指导框架的演进与代码实现。

## 文档速查表

| 文档名称 | 职责简述 | 建议阅读顺序 |
|---|---|---|
| [DOC_CONTRACT.md](DOC_CONTRACT.md) | 定义四份技术文档的内容边界、术语一致性与引用规范，是术语速查的权威来源。 | 1 |
| [01-requirements.md](01-requirements.md) | 定义 OMK `0.1.0` 版本的功能需求、非功能需求与兼容性目标，作为后续设计的基准与约束来源。 | 2 |
| [02-architecture.md](02-architecture.md) | 定义系统四层架构、组件职责、接口契约、运行时数据流与部署视图。 | 3 |
| [03-system-design.md](03-system-design.md) | 在架构基础上展开各模块的接口定义、数据流、状态机与持久化细节。 | 4 |
| [04-functional-design.md](04-functional-design.md) | 定义各 `Skill` 工作流、`Agent` 协作模式、状态管理与通知集成的详细功能规格。 | 5 |
| [.maintenance.md](.maintenance.md) | 规定语义锚点维护、结构一致性版本化、人工审阅周期与门禁脚本升级等维护协议。 | 6 |

## 外部文档索引

- **用户安装与快速开始**：请查阅仓库根目录的 [README_ZH.md](../../README_ZH.md)。
- **官方 Kimi CLI 用户指南**：请查阅 [kimi-cli-docs/zh/](../../kimi-cli-docs/zh/) 目录下的使用说明、配置参考与 FAQ。

## 术语速查

本文档集全文术语须与 [DOC_CONTRACT.md](DOC_CONTRACT.md) 的术语表保持一致；若对专有名词的中文或英文写法有疑问，请优先查阅该文档。

## 维护说明

本文档集的维护协议（语义锚点管理、门禁规则、审阅周期）记录于 [.maintenance.md](.maintenance.md)，文档维护者与核心贡献者在发起变更前请先阅读该文件。
