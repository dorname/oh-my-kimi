---
omk-commit: 990ef862c6a7a8c57c7350169be7091354832b23
---

基于 OMK commit: 990ef862c6a7a8c57c7350169be7091354832b23

# OMK 总体架构文档

本文档为 OMK（`Kimi 编排与多智能体协调`，Oh-My-Kimi）的总体架构文档（ARCH），
定义 `0.1.0` 版本的系统分层、组件职责、接口契约、运行时数据流与部署视图。
所有术语须与 `docs/zh/DOC_CONTRACT.md` 的术语表保持一致，并在正文中以反引号包裹。
本文档是 `Skill/Agent 接口签名` 关注点的规范源。

## 架构概述

OMK 采用四层架构，自上而下分别为 `User 层`、`Orchestration 层`、
`Execution 层` 与 `State 层`。各层之间通过明确定义的接口契约交互，
禁止跨层直接访问内部实现。`README_ZH.md` 的 `架构` 章节
提供了本架构的精简示意图，本文档在此基础上展开各层的职责边界与交互协议。

```
User Input → kimi --agent-file .kimi/agents/agent.yaml
                    → Skill Detection → Agent Orchestration
                    → Tools & State → .omk/ (JSON/Markdown)
```

`User 层` 负责接收原始输入，并将其转换为 `Orchestration 层` 可识别的意图。
输入形态包括纯自然语言、`/skill:<name>` 斜杠命令，
以及由 `Frontmatter` 标识的已加载 `SKILL.md` 内容。
`Orchestration 层` 由 `根 Agent` 主导，依据 `Skill` 触发词或斜杠命令完成意图识别，
随后将任务委派给合适的 `子 Agent`。
`Execution 层` 承载实际的 `工具调用`、代码执行与外部通信，
所有操作均受 `工具安全边界` 约束。
`State 层` 提供跨 `会话` 的持久化能力，确保长周期任务可在中断后恢复，
并为审计与回溯提供数据基础。

## Skill 层

OMK 共提供 36 个 `Skill`，分布于 `skills/<name>/SKILL.md`，
覆盖工作流编排、审查、诊断、知识管理与实用工具五大类别。
每个 `Skill` 以 Markdown 形式组织，其 `Frontmatter` 包含名称、描述与兼容性说明。
`Skill` 的元数据在加载阶段被注入 `系统提示词`，
供 `根 Agent` 在运行时识别与调度。

- **工作流编排**：`autopilot`、`ralph`、`ultrawork`、`team`、`plan`、`ralplan`、`deep-dive`、`ultraqa`、`ccg`、`sciomk`、`self-improve`；
- **审查**：`code-reviewer`、`security-reviewer`；
- **诊断**：`debug`、`trace`、`omk-doctor`；
- **知识管理**：`wiki`、`remember`、`learner`、`writer-memory`；
- **实用工具**：`cancel`、`setup`、`skill`、`skillify`、`verify`、`release`、`mcp-setup`、`configure-notifications`、`external-context`、`project-session-manager`、`deepinit`、`visual-verdict`、`ai-slop-cleaner`、`ask`。

`Skill` 的加载遵循 `kimi-cli-docs/zh/customization/skills.md` 的 `Skill 发现` 章节定义的分层机制：

1. `内置 Skills`：随 Kimi CLI 包安装的基础技能，位于 Kimi 系统目录；
2. `用户级 Skills`：存放于用户主目录的 Kimi 技能搜索路径，如 `~/.kimi/skills/`；
3. `项目级 Skills`：存放于当前项目目录的 Kimi 技能搜索路径，如 `./.kimi/skills/`。

当同名 `Skill` 冲突时，品牌组优先于通用组，
`项目级 Skills` 优先于 `用户级 Skills`，
`用户级 Skills` 优先于 `内置 Skills`。
OMK 的安装器将技能部署到 Kimi 可识别的品牌组目录，
确保加载顺序正确，同时避免向通用组目录写入，
以防止与其他生态的技能发生冲突。

`Skill` 支持两种形态：普通 `Skill` 通过触发词或斜杠命令激活，执行单轮或多轮任务后结束；
`Flow Skill` 通过内嵌的 `BEGIN`/`END` 节点协议定义多步骤自动化工作流，
用于编排多个 `Agent` 的串行或并行执行。

`Skill` 触发词与 `SKILL.md` `Frontmatter` 构成元数据契约。
触发词的设计应避免与常见自然语言表述过度重叠，以降低误激活概率。
当多个触发词同时匹配时，采用最长匹配优先策略。
`Skill` 的 `Frontmatter` 须包含 `name` 与 `description` 字段，
以便在 `Skill 发现` 阶段被正确解析。
`Flow Skill` 还须定义节点间的流转条件与终止判定逻辑。

## Agent 层

OMK 的 `Agent` 系统由 `根 Agent` 与 18 个公开专家 `子 Agent` 构成，
形成单一的调度中心加多专业执行节点的星型拓扑。
`根 Agent` 通过 `--agent-file` 加载 `agents/default/agent.yaml` 启动，
负责统一调度、上下文保持与任务分发。
`agents/default/agent.yaml` 的 `subagents` 配置块
定义了全部 18 个 `子 Agent` 的路径与描述，完整名单如下：

- 构建/分析通道：`coder`、`explore`、`analyst`、`plan`、`architect`、`debugger`、`executor`、`verifier`、`tracer`；
- 审查通道：`code-reviewer`、`security-reviewer`；
- 领域专家：`test-engineer`、`designer`、`writer`、`document-specialist`、`code-simplifier`、`scientist`；
- 协调：`critic`。

`agents/default/system.md` 的 `Agent Catalog` 章节
进一步规定了这些 `Agent` 的角色划分、适用场景与委派规则。
`根 Agent` 依据任务类型选择最合适的 `子 Agent`，
通过 `Agent(subagent_type="...", prompt="...")` 发起调用。
`子 Agent` 在独立上下文中运行，不继承 `根 Agent` 的完整 `上下文`，
仅通过 `prompt` 参数接收必要背景信息。
`子 Agent` 支持前台与 `后台任务` 两种执行模式，
后者适用于安装、构建、测试等可异步完成的长时间操作。

`kimi-cli-docs/zh/customization/agents.md` 的 `自定义 Agent 文件` 章节
说明了配置文件的继承与覆盖机制。
OMK 的 `根 Agent` 配置通过 `system_prompt_args` 注入 `ROLE_ADDITIONAL` 等自定义参数，
与 Kimi CLI 的内置变量协同工作，不得冲突。
`子 Agent` 不可嵌套创建自己的 `子 Agent`，
此限制由 Kimi CLI 原生施加，OMK 须在其文档与提示词中明确声明。
`Agent` 系统须支持 `Plan 模式` 与 `YOLO 模式` 两种审批策略，
以适应不同风险偏好的场景。

`Agent` 配置文件采用 YAML 格式，核心字段包括 `version`、`agent`、
`name`、`system_prompt_path`、`system_prompt_args`、
`tools`、`exclude_tools` 与 `subagents`。
`extend` 字段支持配置继承，允许 `子 Agent` 在复用父配置的基础上进行局部覆盖。
`tools` 列表声明该 `Agent` 可调用的工具集合，
`exclude_tools` 用于从继承配置中移除特定工具。
这种继承机制减少了重复配置，并确保所有 `Agent` 共享统一的安全策略基线。

`根 Agent` 的委派决策遵循以下准则：
当涉及多文件变更、重构、调试、代码审查或规划研究时，优先委派给 `子 Agent`；
当仅为简单文件查找、直接问答或单命令顺序操作时，`根 Agent` 可直接处理。
在共识规划模式下，`根 Agent` 的角色严格限定为协调者与综合者，
禁止直接创建规划内容或执行实现代码。

## Python 工具层

OMK 的 Python 工具包位于 `omk/` 目录，
作为 `Execution 层` 的辅助设施，提供状态读写、通知发送与更新检查能力。
入口命令由 `pyproject.toml` 的 `project.scripts` 注册为 `omk`，
对应 `omk.cli` 模块。Python 最低版本要求为 `>=3.9`。

核心模块职责划分如下：

- `omk/cli.py`：提供 `omk state`、`omk notifier`、`omk updater` 等子命令，
  是用户与状态管理层、通知模块、更新模块交互的主要入口；
- `omk/state.py`：管理 `状态目录` 的创建、读取、写入与清除，
  维护 `DEFAULT_STATE_DIR` 等路径约定；
- `omk/notifier.py`：封装 Telegram Bot API、Discord Webhook、Slack Webhook
  三种通知渠道的消息发送逻辑；
- `omk/updater.py`：执行本地版本与远程仓库发布信息的比对，
  并向用户报告更新可用性。

`scripts/` 目录下的 Shell 脚本作为 Python 工具层的补充，
承担通知发送、更新检查、结构化代码搜索、语言服务器诊断与速率限制处理等职责。
所有脚本执行须遵循 `Kimi Code CLI` 的 `Shell` 审批机制，不得绕过用户授权。
脚本优先使用 POSIX 标准语法，并在非标准环境下给出明确错误提示。
更新检查脚本支持从远程仓库获取最新版本信息并与本地版本比对。

## 状态管理层

OMK 在项目目录的 `.omk/` 下建立 `状态目录`，用于持久化运行时数据。
状态管理层是 `State 层` 的核心实现，支持跨 `会话` 恢复与查询，
确保长周期任务的连续性。状态文件须采用人类可读的文本格式，
便于调试与版本控制。

目录结构及其用途如下：

| 路径 | 用途 |
|------|------|
| `.omk/state/` | 模式状态文件（JSON），记录各 `Skill` 或模式的激活状态 |
| `.omk/state/sessions/` | `会话` 跟踪元数据，保存分支、worktree 与任务进度 |
| `.omk/notepad.md` | `记事本`，用于持久化笔记与临时结论 |
| `.omk/project-memory.json` | `项目记忆`，保存跨会话的可复用知识与术语表 |
| `.omk/plans/` | 规划文档，存放由 `plan`、`ralplan` 等技能生成的结构化方案 |
| `.omk/wiki/` | `知识库`，分层组织的 Markdown 文档集合 |
| `.omk/logs/` | 审计日志，记录关键操作与 `Agent` 委派历史 |

状态生命周期遵循 `agents/default/system.md` 中定义的三阶段协议：

1. **启动**：模式或任务开始时，向对应状态文件写入 `active: true`；
2. **完成**：正常结束后，将同一状态文件更新为 `active: false`；
3. **取消**：用户主动取消或异常中断时，清除状态文件或标记为取消。

状态读写操作须通过 `omk state` 命令或等效模块接口完成，
禁止直接绕过管理模块操作文件，以确保格式一致性。
`项目记忆` 与 `记事本` 使得多次 `会话` 之间能够继承已确认的结论与风格指南，
降低重复沟通成本。
规划文档目录 `.omk/plans/` 用于存放共识规划或独立规划的结果，
支持版本控制与团队协作。
审计日志目录 `.omk/logs/` 记录关键决策与 `Agent` 委派历史，
为事后回溯提供证据链。

## 运行时数据流

OMK 的典型运行时数据流如下，涵盖从用户输入到状态持久化的完整闭环：

1. **用户输入**：用户在 `Shell 模式` 下输入自然语言请求，
   或通过 `/skill:<name>`、`/flow:<name>` 斜杠命令直接加载 `Skill`。
   若输入以 `---` `Frontmatter` 开头，
   则视为已加载的 `SKILL.md` 内容，立即进入激活态；
2. **Skill 检测**：`根 Agent` 检测输入中的触发词。
   若匹配，则读取对应 `SKILL.md` 并将其内容作为 `User 消息` 注入当前 `会话`。
   对于 `Flow Skill`，进一步解析其内嵌的流程节点；
3. **Agent 编排**：依据 `Skill` 工作流或 `Agent Catalog` 的委派规则，
   `根 Agent` 选择目标 `子 Agent` 并发起 `Agent` 调用。
   若任务包含多个独立子任务且预计耗时超过 30 秒，
   `根 Agent` 应优先并行派发；
4. **工具执行**：`子 Agent` 在独立上下文中执行 `工具调用`，
   包括 `Shell`、`ReadFile`、`WriteFile`、`SearchWeb`、`FetchURL` 等。
   所有文件写入与 `Shell` 命令均受 `工具安全边界` 约束，敏感文件始终被过滤；
5. **状态更新**：任务进展、模式激活状态、审计信息与错误回写
   被写入 `.omk/` 下的对应文件，完成一次完整的运行时闭环。

`后台任务` 通过 `run_in_background=true` 启动后，
其状态同样被纳入 `状态目录` 管理，
支持通过 `TaskOutput` 与 `TaskStop` 进行异步查询与终止。
失败任务的状态回写使得调用方可以通过 `omk state read` 查询失败原因，
并决定是否重试。依赖任务须按序执行，独立任务推荐并行以提升效率。

## 部署视图

OMK 的部署通过 `install.sh` 与 `uninstall.sh` 完成，
支持三种安装粒度，覆盖不同隔离需求：

- **全局安装**：将 `Skill` 与 `Agent` 配置部署到用户级 Kimi 目录，
  并将 `omk` Python 包安装至当前 Python 环境，
  适用于个人开发机在多个项目间共享 OMK 能力；
- **项目本地安装**：将 `Skill` 与 `Agent` 配置部署到当前项目目录的
  `./.kimi/skills/` 与 `./.kimi/agents/`，不影响其他项目，
  适用于团队协作中对版本一致性有严格要求的场景；
- **指定目录安装**：向任意目标项目的 Kimi 目录执行部署，
  适用于为多个独立代码库批量配置 OMK 的情形。

安装器在执行前显示将要安装的文件清单，
并在发生冲突时提供覆盖或跳过选项。
卸载脚本支持保留 `.omk/` 运行时状态目录的选项，防止误删用户数据。
安装与卸载流程的详细行为需求与退出码定义
属于 `CLI 命令矩阵` 与 `错误码体系` 关注点，
参见 `docs/zh/01-requirements.md` 的 `功能需求` 章节。

OMK 的验证流程以 `--agent-file` 路径启动后调用自定义 `子 Agent`
作为最小可工作证明。兼容性验证须以此路径为基准进行冒烟测试。
安装器应避免向通用组目录写入，
以防止与 Claude 或 Codex 生态的技能发生冲突。
卸载流程在移除文件前须明确提示用户，并提供保留状态目录的选项。

## 兼容性约束

OMK 的兼容性目标为 `Kimi Code CLI` `1.36.0`。
参见 `docs/zh/01-requirements.md` 的 `兼容性目标` 章节。
框架仅依赖 Kimi CLI 原生能力，保持零外部模型依赖。
Python 运行时版本须满足 `>=3.9`，
以确保在主流操作系统与长期支持环境中的可部署性。
当 Kimi CLI 发布新版本时，
OMK 应能在不修改核心代码的前提下，
通过调整配置或 `Agent` `提示词` 完成适配。
`--agent-file` 加载自定义 `根 Agent` 是唯一的官方引导路径，
纯 `kimi` 命令不在 OMK 支持范围内。

本文档使用的所有术语定义、事实清单与引用规范详见 `docs/zh/DOC_CONTRACT.md`。
若事实清单中的客观数据发生变更，须同步更新 `DOC_CONTRACT.md` 并重新生成本文档的 `omk-commit`，
随后运行契约检查脚本验证一致性。
