---
omk-commit: 990ef862c6a7a8c57c7350169be7091354832b23
---

基于 OMK commit: 990ef862c6a7a8c57c7350169be7091354832b23

# OMK 功能设计文档

本文档为 OMK（`Kimi 编排与多智能体协调`，Oh-My-Kimi）的功能设计文档（FUNC），
定义 `0.1.0` 版本各 `Skill` 工作流、`Agent` 协作模式、状态管理与通知集成的详细功能规格。
所有术语须与 `docs/zh/DOC_CONTRACT.md` 的术语表保持一致，并在正文中以反引号包裹。

## Skill 系统功能设计

### 触发机制

`Skill` 支持三种激活路径，按优先级由高到低依次为：

1. **斜杠命令加载**：用户输入 `/skill:<name>` 或 `/flow:<name>` 时，
   Kimi CLI 直接将对应 `SKILL.md` 的全文内容作为 `User 消息` 注入当前 `会话`；
2. **Frontmatter 隐式加载**：当 `User 消息` 以 `---` 开头的 YAML `Frontmatter`
   （包含 `name` 与 `description` 字段）起始时，`根 Agent` 立即将该消息视为已加载的 `Skill` 内容，
   跳过触发词检测，直接执行其工作流；
3. **自然语言触发词匹配**：当用户输入的纯文本不包含已加载的 `SKILL.md` 时，
   `根 Agent` 扫描输入中的隐式触发词。触发词匹配规则如下：
   - 不区分大小写，可在消息任意位置匹配；
   - 多个触发词同时命中时，采用最长匹配优先策略；
   - 触发词后的剩余文本自动提取为任务描述。

### 标准 Skill 与 Flow Skill

`Skill` 存在两种形态，参见 `docs/zh/02-architecture.md` 的 `Skill 层` 章节：

- **标准 `Skill`**：通过触发词或斜杠命令激活，执行单轮或多轮任务后正常结束。
  其 `SKILL.md` 的 `Frontmatter` 须包含 `name`、`description` 与 `metadata.triggers`；
- **`Flow Skill`**：内嵌 `BEGIN`/`END` 节点协议，定义多步骤自动化工作流，
  用于编排多个 `Agent` 的串行或并行执行。`Flow Skill` 除标准 `Frontmatter` 外，
  还须定义节点间的流转条件与终止判定逻辑。

### Skill 分类

OMK 的 36 个 `Skill` 按功能属性划分为三大类：

| 类别 | 说明 | 代表 `Skill` |
|------|------|-------------|
| 工作流编排 | 驱动多阶段、多 `Agent` 的复杂任务流程 | `plan`、`ralph`、`autopilot`、`ultrawork`、`team`、`deep-dive`、`ultraqa` |
| 实用工具 | 提供单次调用即可完成的辅助能力 | `cancel`、`verify`、`trace`、`setup`、`skill`、`mcp-setup`、`configure-notifications` |
| 记忆与知识 | 管理跨 `会话` 的持久化知识与经验 | `wiki`、`remember`、`learner`、`writer-memory` |

## 核心 Skill 工作流详设

### `plan` — 战略规划四模式工作流

**触发词**：`plan this`、`plan the`、`let's plan`、`plan`、`review this plan`

`plan` 提供四种互斥执行模式，由 `根 Agent` 根据请求特征自动选择：

- **Interview 模式**（默认，针对宽泛请求）：通过 `AskUserQuestion` 逐轮澄清需求，
  每次仅提一个问题，并在询问代码库相关问题时先委派 `explore` `子 Agent` 收集事实；
- **Direct 模式**（`--direct` 或细节充分的请求）：跳过访谈，直接生成可执行规划；
- **Consensus 模式**（`--consensus` 或触发词 `ralplan`）：
  严格遵循 `Planner → Architect → Critic` 的顺序循环，最多 5 轮，
  `根 Agent` 仅作为协调者，禁止直接生成规划内容或执行代码；
- **Review 模式**（`--review` 或 `review this plan`）：从 `.omk/plans/` 读取既有规划，
  委派 `Critic` 评审并输出 `APPROVED`/`REVISE`/`REJECT` 结论。

### `ralph` — PRD 驱动持久循环

**触发词**：`ralph`、`don't stop`、`must complete`、`finish this`、`keep going until done`

`ralph` 以 `prd.json` 为单一事实源，通过 `Ralph 循环` 保证任务必达完成态：

1. **PRD 初始化**：若 `.omk/prd.json` 不存在，自动生成骨架并按任务特征细化验收标准；
2. **故事选取**：每次迭代读取 `prd.json`，选择优先级最高且 `passes: false` 的用户故事；
3. **实现与验证**：委派 `子 Agent` 实现当前故事，运行测试、构建与类型检查，
   未达标则继续修复，禁止标记未完成的故事为通过；
4. **评审与清理**：全部故事通过后，由选定评审人（默认 `architect`，可配置 `--critic`）
   按具体验收标准执行强制验证，随后无条件运行 `ai-slop-cleaner` 清理变更文件，
   并通过回归测试确认无退化；
5. **状态回写**：全过程通过 `.omk/state/ralph-state.json` 记录激活状态与迭代计数。

### `autopilot` — 全自主执行管道

**触发词**：`autopilot`、`auto pilot`、`autonomous`、`build me`、`create me`、
`make me`、`full auto`、`handle it all`、`I want a`、`I want an`

`autopilot` 将用户的两三行产品描述转化为可运行的代码，共包含 6 个阶段：

1. **Expansion**：委派 `analyst` 与 `architect` 提取需求并输出技术规格；
2. **Planning**：由 `architect` 制定实现规划，经 `critic` 评审；
3. **Execution**：并行委派多个 `executor` 执行子任务，独立任务同时触发；
4. **QA**：最多 5 轮测试-修复循环，同一错误连续 3 次未修复则上报根本问题；
5. **Validation**：并行发起架构、安全与代码质量三重评审，全部通过方可进入清理；
6. **Cleanup**：删除所有模式状态文件，调用 `cancel` 完成干净退出。

### `ultrawork` — 并行 Agent 编排

**触发词**：`ultrawork`、`ulw`、`parallel`

`ultrawork` 作为并行执行引擎，不负责持久化与验证循环，其核心规则为：

- 识别任务间的依赖关系，独立任务通过 `Agent` 工具同时发起，禁止串行等待；
- 预计耗时超过 30 秒的操作（安装、构建、测试套件）使用 `run_in_background=true`；
- 快速命令（`git status`、文件读取）保持前台执行；
- 完成后执行轻量级验证：构建通过、受影响测试通过、无新增错误。

### `team` — 协调式多 Agent 共享任务列表

**触发词**：`team`

`team` 采用分阶段管道 `team-plan → team-exec → team-verify → team-fix（循环）`：

1. **解析输入**：提取 `Agent` 数量（1–6，默认自动分片）、`Agent` 类型与任务描述；
2. **分析与分解**：委派 `explore` 或 `architect` 将任务拆分为文件级或模块级子任务，
   写入 `.omk/state/team-tasks.json`；
3. **并行执行**：同时启动所有无依赖的子任务 `Agent` 调用，各 `子 Agent` 在独立上下文中工作；
4. **监控与协调**：追踪完成状态，处理失败重试、重新分配或跳过；
5. **验证**：运行构建与测试，按需引入 `verifier`、`code-reviewer` 或 `security-reviewer`；
6. **完成报告**：验证通过后汇总结果并清理 `team-state.json`。

支持 `team ralph` 组合模式，将 `team` 管道嵌入 `ralph` 的持久循环中。

### `deep-dive` — 两阶段深度分析管道

**触发词**：`deep dive`、`deep-dive`

`deep-dive` 将技术根因调查与需求澄清串联为两阶段管道：

1. **Stage 1 — Trace**：调用 `trace` 技能形成多假设竞争分析，追溯症状到根因；
2. **Stage 2 — Deep Interview**：基于 Stage 1 发现，通过 `deep-interview` 技能澄清需求缺口；
3. **三点注入**：在最终报告中注入根因、需求缺口与推荐解决方案三项关键洞察。

输出保存至 `.omk/research/deep-dive-<topic>.md`。

### `ultraqa` — QA 循环工作流

**触发词**：`ultraqa`、`qa cycle`

`ultraqa` 执行结构化的测试-验证-修复循环：

1. 运行测试套件并收集失败用例；
2. 分类失败原因（回归缺陷、新 bug、测试本身问题、预期变更）；
3. 按优先级逐条修复，禁止批量混杂无关修复；
4. 重新运行测试验证修复效果；
5. 重复循环直至全部通过或达到最大循环次数（默认 5 次）。

同一错误连续 3 次复现则停止循环并上报根本问题。状态维护于 `.omk/state/ultraqa-state.json`。

### `trace` — 证据驱动追溯

**触发词**：`trace`、`trace this`

`trace` 以竞争假设方法进行因果调查：

1. **观察**：收集错误信息、日志、近期变更与环境状态；
2. **假设**：至少形成 3 个竞争根因假设；
3. **测试**：为每个假设设计可证实或证伪的证据；
4. **收集证据**：运行实验、读取日志、检查代码历史；
5. **评估**：按证据强度为各假设评分；
6. **结论与建议**：输出最可能根因（附置信度）与修复方案。

追溯报告保存至 `.omk/logs/trace-<timestamp>.md`。

### `verify` — 变更验证工作流

**触发词**：`verify`、`verify that`

`verify` 在任务声称完成前执行六步验证：

1. **构建检查**：运行项目构建命令并确认成功；
2. **测试检查**：运行相关测试并确认通过；
3. **Lint 检查**：运行代码风格检查，确认无新增错误；
4. **类型检查**：运行类型系统检查（如适用）；
5. **手动验证**：确认变更确实解决了声明的问题；
6. **回归检查**：确认未破坏现有功能。

复杂场景可委派 `verifier` `子 Agent` 执行深度验证。

### `cancel` — 模式取消与状态清理

**触发词**：`cancel`、`stop`、`abort`

`cancel` 负责安全终止任意活跃 OMK 模式：

1. 读取 `.omk/state/` 识别当前 `active: true` 的模式；
2. 对每个活跃模式，将其状态文件更新为 `active: false` 或直接移除；
3. 清理模式相关的临时文件；
4. 向用户报告已取消的模式列表。

适用场景包括：全部任务完成并验证后的干净退出、工作阻塞无法继续、用户主动喊停。

## Agent 协作模式设计

本节所述协作模式的功能规格与 `docs/zh/02-architecture.md` 的 `Agent 层` 章节相互补充，
`02-architecture.md` 定义接口签名与拓扑结构，本文档聚焦运行时协作行为。

### 根 Agent 编排（只读协调者 vs 执行者）

`根 Agent` 承担两种互斥运行时角色：

- **执行者角色**：处理简单文件查找、直接问答或单命令顺序操作，
  直接使用 `ReadFile`、`Shell` 等工具完成；
- **只读协调者角色**：在 `Consensus 模式`（`ralplan` / `plan --consensus`）下，
  `根 Agent` 严格限定为协调者与综合者，禁止直接创建规划内容、执行代码或运行验证命令。
  此设计强制多视角验证，防止能力强模型绕过子代理自行完成工作。

### 子 Agent 委派

`根 Agent` 通过 `Agent(subagent_type="<name>", prompt="...")` 发起委派，
`subagent_type` 的取值范围由 `agents/default/agent.yaml` 的 `subagents` 配置块定义的 18 个公开 `子 Agent` 决定。

委派决策遵循 `docs/zh/02-architecture.md` 的 `Agent 层` 章节所述准则：

- 涉及多文件变更、重构、调试、代码审查或规划研究时，优先委派给 `子 Agent`；
- 简单查找、直接问答或单命令顺序操作时，`根 Agent` 可直接处理；
- `子 Agent` 在独立上下文中运行，不继承 `根 Agent` 的完整 `上下文`，
  仅通过 `prompt` 参数接收必要背景信息；
- `子 Agent` 支持前台与 `后台任务` 两种执行模式，后者适用于安装、构建、测试等长时间操作。

### 共识模式（Planner → Architect → Critic 顺序执行）

`共识模式`是 `plan` 与 `ralplan` 的核心协作形态，其功能约束如下：

- **严格串行**：`Planner` 输出 → `Architect` 评审 → `Critic` 审计，
  三阶段必须顺序执行，`根 Agent` 须等待前一 `子 Agent` 返回后方可发起下一阶段调用，
  禁止并行同时调用多个评审角色；
- **角色隔离**：`根 Agent` 不得替代任何子代理执行其专属职责，
  即禁止自行生成规划、自行进行架构评审或自行完成质量批判；
- **循环上限**：若 `Critic` 拒绝，最多允许 5 轮重新修订循环，
  超过上限则呈现最佳版本并移交用户决策；
- **成果保存**：最终通过的规划须保存至 `.omk/plans/`，
  执行须移交给 `ralph` 或 `team`，禁止在规划 `Agent` 内直接实现。

### 并行模式（`ultrawork` 并行 Agent 调用）

与共识模式的强制串行相反，`ultrawork` 与 `team` 启用并行协作模式：

- 当存在 2 个及以上相互独立的子任务，且每个任务预计耗时超过 30 秒时，
  `根 Agent` 应在同一响应中同时输出多个 `Agent` 工具调用；
- 依赖任务必须按序执行，禁止在前置任务完成前启动后续任务；
- 并行执行期间，`根 Agent` 通过收集各 `子 Agent` 的返回结果进行汇总与协调。

## 状态管理功能设计

状态管理功能的具体 Schema 定义参见 `docs/zh/03-system-design.md`，
本文档聚焦各状态组件的运行时功能行为。

### 模式状态

每个活跃 `Skill` 或模式在 `.omk/state/<mode>-state.json` 中维护独立状态文件，
遵循三阶段生命周期协议：

1. **启动**：写入 `active: true` 及模式专属字段（如当前阶段、迭代计数）；
2. **完成**：更新为 `active: false`；
3. **取消**：用户主动取消或异常中断时，清除状态文件或标记为取消。

状态读写须通过 `omk state` 命令或等效模块接口完成，禁止直接绕过管理模块操作文件。

### 记事本

`.omk/notepad.md` 提供持久化笔记功能，用于记录跨 `轮次` 的临时结论、
待办事项或上下文摘要。`根 Agent` 可在任意时刻读取或追加内容，
作为多轮对话中的短期记忆补充。

### 项目记忆

`.omk/project-memory.json` 保存跨 `会话` 的可复用知识，包括术语表、
代码风格约定、已确认的技术决策与架构约束。新 `会话` 启动时，
`根 Agent` 可主动读取该项目记忆，降低重复沟通成本。

### 知识库

`.omk/wiki/` 为分层组织的 Markdown 文档集合，通过 `wiki` `Skill` 进行管理。
支持添加、查询与更新操作，用于沉淀长期项目知识，供不同 `会话` 共享。

## 通知与集成功能设计

### 通知渠道

OMK 的通知功能由 `omk/notifier.py` 提供，支持三种推送渠道：

| 渠道 | 配置方式 | 典型场景 |
|------|---------|---------|
| Telegram Bot API | 环境变量 `OMK_TELEGRAM_TOKEN`、`OMK_TELEGRAM_CHAT` | 长任务完成、异常中断、审批请求 |
| Discord Webhook | 环境变量 `OMK_DISCORD_WEBHOOK` | 团队协作频道推送 |
| Slack Webhook | 环境变量 `OMK_SLACK_WEBHOOK` | 企业工作区集成 |

消息发送须包含重试策略与错误降级处理：当某一渠道连续失败达到阈值时，
记录错误日志并静默跳过，避免阻塞主任务流程。
通知消息格式须包含任务标识、状态摘要与关键结论，
禁止在通知中泄露敏感文件内容或 `API 密钥`。

### MCP 外部工具集成

`MCP` 扩展了 `Execution 层` 的工具边界，使 `子 Agent` 能够调用外部服务与专用工具。
`mcp-setup` `Skill` 负责引导用户完成 `MCP` 配置，包括服务端点注册、
认证信息录入与可用工具枚举。配置完成后，`Agent` 可在 `工具调用` 中
通过标准接口访问 `MCP` 提供的远程能力，所有调用均受 `工具安全边界` 约束。
