# OMK Skill 业务逻辑优化专项报告

> **审计焦点**：36 个 Skill 的业务逻辑设计、工作流效率、功能边界与触发词策略  
> **合规基线**：`kimi-cli-docs/zh/` 官方规则（详见文末「官方业务逻辑设计约束速查」）  
> **交付原则**：先报告，后执行；所有建议均以官方规则为上限约束  
> **生成日期**：2025-05-15

---

## 执行摘要

本次审计从**业务逻辑视角**（而非格式合规视角）扫描了 36 个 Skill，识别出 **27 项优化机会**，分布在 6 个维度：

| 维度 | 数量 | 最高风险项 |
|------|------|-----------|
| 触发词冲突 | 6 | `autopilot` 的 `I want a` / `build me` 会在日常对话中误触发 |
| 功能重叠/冗余 | 6 | `ralplan` 与 `plan --consensus` 是同一工作流的双份拷贝 |
| Skill 粒度不当 | 5 | `verify` 仅 42 行，是 6 个 Skill 都在内联复制的 checklist |
| 工作流低效 | 3 | `self-improve` 未并行化候选评估，`team` 监控阶段串行轮询 |
| 合规风险 | 3 | 大量 `Agent` 调用示例缺少官方要求的 `description` 参数 |
| 缺失 Skill | 4 | `code-reviewer` / `security-reviewer` Agent 无对应 Skill 入口 |

**核心建议方向**：
1. **删除 4 个 Skill**（`ralplan`、`omk-teams`、`hud`、`deep-dive`），将价值并入其他 Skill。
2. **合并 3 组 Skill**（`learner`→`skillify`、`verify`→`ultraqa`、`wiki`↔`remember` 边界澄清）。
3. **重构 1 个 Skill**（`autopilot` 从"重新实现"改为"显式调用"子 Skill）。
4. **收紧 6 组触发词**，移除日常对话中极易误触的单字/短句触发。
5. **补充 3 个新 Skill**（`security-review`、`code-review`、`refactor`）。

---

## 1. 触发词冲突审计（6 项，高影响）

> **官方规则依据**：`kimi-cli-docs/zh/customization/skills.md` 规定 Skill 通过自然语言触发词唤醒，但未限制触发词长度；因此触发词设计属于业务逻辑策略问题。过宽的触发词会违反「AskUserQuestion should not be overused」的交互设计精神（`agents.md`），因为误触后 AI 会错误地进入工作流，反而需要更多澄清提问来撤回。

### 1.1 `autopilot` — 灾难级宽泛触发
- **当前触发词**：`autopilot`, `auto pilot`, `autonomous`, `build me`, `create me`, `make me`, `full auto`, `handle it all`, `I want a`, `I want an`
- **风险示例**：
  - "I want a coffee" → 触发 autopilot
  - "Build me a fire" → 触发 autopilot
  - "Make me a sandwich" → 触发 autopilot
  - "I can't handle it all today" → 触发 autopilot
- **业务逻辑影响**：autopilot 是一个 5 阶段重型流水线（分析→规划→并行执行→QA→验证），误触发一次即消耗大量 token 和用户时间。
- **优化建议**：
  - **移除**：`I want a`, `I want an`, `build me`, `create me`, `make me`
  - **保留**：`autopilot`, `auto pilot`, `autonomous`, `full auto`, `handle it all`
  - **理由**：前 5 个触发词是纯日常动词短语，后 5 个包含专有名词或特定语义场，误触率显著降低。

### 1.2 `ultrawork` — `parallel` 在技术语境中过度敏感
- **当前触发词**：`ultrawork`, `ulw`, `parallel`
- **风险示例**：
  - "Run these tests in parallel" → 触发 ultrawork
  - "Parallel arrays are faster" → 触发 ultrawork
  - "I need parallel processing" → 触发 ultrawork（可能正确，也可能只是讨论架构）
- **业务逻辑影响**：`ultrawork` 会启动并行 Agent 执行，若用户只是在讨论技术方案而非请求执行，误触会造成资源浪费。
- **优化建议**：
  - **移除**：`parallel`
  - **保留**：`ultrawork`, `ulw`
  - **补充**：若希望保留自然语言入口，可改为多词触发如 `parallel execution` 或 `parallel agents`。

### 1.3 `cancel` — `stop` 在日常对话中高频出现
- **当前触发词**：`cancel`, `stop`, `abort`
- **风险示例**：
  - "Stop using that approach" → 触发 cancel
  - "I want to stop here and think" → 触发 cancel
  - "Stop the server before deploying" → 触发 cancel
- **业务逻辑影响**：`cancel` 会清除活跃模式状态（autopilot、ralph 等），误触会丢失进行中的上下文。
- **优化建议**：
  - **移除**：`stop`
  - **保留**：`cancel`, `abort`
  - **理由**：`cancel` 和 `abort` 在软件工作流中有明确的"取消操作"语义；`stop` 过于通用。

### 1.4 `ask` — 单字 `ask` 几乎无处不在
- **当前触发词**：`ask`, `ask codex`, `ask gemini`
- **风险示例**：
  - "I wanted to ask you something" → 触发 ask
  - "Ask the user for confirmation" → 触发 ask
  - "Can I ask a question?" → 触发 ask
- **业务逻辑影响**：`ask` Skill 会尝试路由到特定模型视角（Claude/Codex/Gemini），误触会在普通对话中插入模型切换逻辑。
- **优化建议**：
  - **移除**：`ask`
  - **保留**：`ask codex`, `ask gemini`
  - **补充**：可新增 `ask claude` 以覆盖完整的三模型路由。

### 1.5 `plan` — 单字 `plan` 与日常计划用语冲突
- **当前触发词**：`plan this`, `plan the`, `let's plan`, `plan`, `review this plan`
- **风险示例**：
  - "I plan to refactor this next week" → 触发 plan
  - "My plan is to use Redis" → 触发 plan
- **业务逻辑影响**：`plan` 会进入 Plan Mode（只读工具，无法修改文件），误触后用户需要额外步骤退出。
- **优化建议**：
  - **移除**：`plan`
  - **保留**：`plan this`, `plan the`, `let's plan`, `review this plan`
  - **理由**：多词触发天然带有"请求 AI 做规划"的祈使语义，单字 `plan` 则更多是用户陈述自己的意图。

### 1.6 `skill` / `skills` — 元讨论中频繁命中
- **当前触发词**：`skill`, `skills`, `manage skills`
- **风险示例**：
  - "What skills do you have?" → 触发 skill
  - "This is a skill issue" → 触发 skill
- **业务逻辑影响**：较低，因为 `skill` Skill 只是管理界面，不会启动重型工作流。但会干扰自然对话流。
- **优化建议**：
  - **移除**：`skill`, `skills`
  - **保留**：`manage skills`

---

## 2. 功能重叠/冗余审计（6 项）

### 2.1 `ralplan` 是 `plan --consensus` 的逐字副本
- **证据**：`ralplan/SKILL.md` 173 行，`plan/SKILL.md` 173 行。`ralplan` 在正文中自述为 "a shorthand alias for `plan --consensus`"，其工作流（Planner→Architect→Critic 循环、最大 5 轮迭代、`--interactive`/`--deliberate` 标志、结束后交给 `team` 或 `ralph`）与 `plan` 的 Consensus Mode 章节完全一致。
- **维护风险**：任何对共识规划流程的更新必须同时修改两个文件，极易产生漂移。
- **优化建议**：
  - **删除** `skills/ralplan/` 目录。
  - 将 `ralplan`、`consensus plan` 作为别名触发词并入 `plan/SKILL.md` 的 frontmatter。
  - `plan` Skill 已原生支持 `--consensus` 模式，无功能损失。
- **合规性**：`skills.md` 允许通过触发词别名调用同一 Skill，不违反任何规则。

### 2.2 `autopilot` 内联复现了 6+ 个 Skill 的核心工作流
- **内联复现映射**：

| autopilot 阶段 | 等价 Skill | 复现内容 |
|---------------|-----------|---------|
| Phase 0 需求扩展 | `deep-interview` + `plan` | 访谈+规格化 |
| Phase 1 技术规划 | `plan` (direct) + `critic` | 规划+评审 |
| Phase 2 并行执行 | `ultrawork` | 并行 Agent 执行 |
| Phase 3 QA 循环 | `ultraqa` | 测试→修复→重测 |
| Phase 4 多视角验证 | `team` (team-verify) + `ralph` | 验证+Reviewer 签字 |
| Phase 5 清理 | `cancel` | 模式退出 |

- **维护风险**：`autopilot` 是目前第二大的 Skill（158 行）。若 `ultrawork`、`ultraqa`、`team` 任何一者更新了并行策略或验证清单，`autopilot` 会立即过时。
- **优化建议**：
  - 将 `autopilot` 重构为**元编排 Skill**（Meta-Skill），不再重述子 Skill 的内部步骤，而是显式调用：
    - "若 `spec.md` 不存在，先加载并执行 `deep-interview` Skill"
    - "执行 `plan` Skill（direct 模式）生成实施计划"
    - "执行 `ultrawork` Skill 完成并行开发"
    - "执行 `ultraqa` Skill 完成 QA 循环"
    - "执行 `team` Skill（verify 阶段）完成多视角验证"
  - 预期可从 ~158 行压缩至 ~80 行，并彻底消除漂移风险。
- **合规性**：`agents.md` 允许 Skill 内容中提及并使用其他 Skill 的 `/skill:<name>` 或 `/flow:<name>` 调用方式，不视为嵌套 `Agent` 违规。

### 2.3 `deep-dive` 是 `trace` + `deep-interview` 的 trivial wrapper
- **证据**：`deep-dive/SKILL.md` 共 54 行，核心内容仅为：
  1. Stage 1 — 使用 `trace` Skill
  2. Stage 2 — 使用 `deep-interview` Skill
  3. Stage 3 — 注入 3 条洞察
- **业务逻辑价值**：无独特工作流，无状态管理，无差异化策略。
- **优化建议**：
  - **删除** `skills/deep-dive/`。
  - 将内容合并到 `trace/SKILL.md` 作为 `--deep` 模式或 "Deep Trace" 子章节。
  - 或合并到 `deep-interview/SKILL.md` 作为 "事后调试访谈" 模式。

### 2.4 `learner` 与 `skillify` 功能相同
- **证据**：两者都是"从对话中提取可复用工作流并保存为 SKILL.md"。
  - `learner`：65 行，4 步（识别模式→写 SKILL.md→保存到目录→验证）。
  - `skillify`：41 行，4 步（识别工作流→写 SKILL.md→保存到目录→验证）。
- **差异**：`skillify` 的动词更主动（"skillify"），`learner` 更被动（"learn"）。业务逻辑无实质区别。
- **优化建议**：
  - **删除** `skills/learner/`。
  - 将 `learner`、`extract skill`、`learn from this` 作为别名触发词并入 `skillify/SKILL.md`。
  - 保留 `skillify`（更短的文件，更主动的命名）。

### 2.5 `wiki` 与 `remember` 边界模糊
- **证据**：`remember/SKILL.md` 的决策树明确将部分知识路由到 `.omk/wiki/`，而这正是 `wiki` 的域。`remember` 本质上是一个"路由决策器"，有时直接操作 `wiki` 的存储位置。
- **现状问题**：两个 Skill 都没有 `Do Not Use When` 章节来澄清边界（`remember` 和 `wiki` 均缺失该章节）。
- **优化建议**：
  - **不删除**，但**澄清边界**：
    - `remember/SKILL.md` 新增 `Do Not Use When`："若你已确定知识应存入 `.omk/wiki/`，请直接使用 `wiki` Skill 而非本 Skill。"
    - `wiki/SKILL.md` 新增 `Do Not Use When`："若你不确定知识应存入何处（wiki、memory、还是其他），先使用 `remember` 进行路由决策。"

### 2.6 验证清单在 6 个 Skill 中被重复内联
- **出现位置**：`verify`, `ultraqa`, `ralph`, `autopilot`, `team`, `ai-slop-cleaner`
- **清单内容**（大致）：build → test → lint → typecheck → manual check → regression
- **维护风险**：任何对验证步骤的增删（如添加 `security-scan`）需要同时修改 6 个文件。
- **优化建议**：
  - 将 `verify` 提升为** canonical 验证 Skill**。
  - 其余 5 个 Skill 不再内联清单，而是显式说："调用 `verify` Skill 执行验证清单"。
  - `ultraqa` 应专注于"循环逻辑"（测试→修复→重测），`verify` 负责"单次验证通过"。

---

## 3. Skill 粒度审计（5 项）

> **官方规则依据**：`skills.md` 建议 `SKILL.md` 保持在 500 行以内，但未规定下限。然而，过小的 Skill 会增加用户的认知负担（需要记住更多 Skill 名称），且易造成触发词 namespace 污染。

### 3.1 `verify` — 42 行，仅一个 checklist
- **分析**：无独特状态管理，无条件分支，无错误处理策略。本质上是一段被 6 个 Skill 重复内联的公共子程序。
- **建议**：并入 `ultraqa` 作为其 "Verification Pass" 章节，或作为 `ralph` 的 "Reviewer Verification" 子程序。若保留独立，至少应扩展至包含：不同技术栈的验证变体（Python/Node/Go/Rust）、失败时的重试策略、与 CI 的集成方式。

### 3.2 `deep-dive` — 54 行，无独特逻辑
- **分析**：已在「功能重叠」中讨论。作为独立 Skill 的附加值不足。
- **建议**：删除或并入 `trace`。

### 3.3 `self-improve` — 47 行，过于模糊
- **分析**：声称实现"进化式改进"（生成 N 候选→评估→选择最优），但未定义：
  - N 的取值策略
  - 突变/变异策略
  - 锦标赛规模或选择压力
  - 收敛判定标准
  - 适应度函数的具体定义
- **建议**：
  - **方案 A**：大幅扩展至 150+ 行，给出具体的进化算法参数和并行评估模式。
  - **方案 B**：降级为内部模式文档（非用户-facing Skill），由 `autopilot` 或 `ralph` 在可选的"优化轮次"中引用。方案 B 更安全，因为进化算法在交互式 CLI 中极易因评估成本过高而失控。

### 3.4 `hud` — 39 行，已自我声明不支持
- **分析**：正文明确说 "Kimi CLI does not support stdin status bars"。Skill 仅指向状态文件和进度文件的位置，属于参考文档而非工作流 Skill。
- **建议**：**删除** `skills/hud/`。内容迁移至 `skills/debug/SKILL.md` 的 "检查 OMK 状态" 子章节，或写入项目 README。

### 3.5 `autopilot` — 158 行，过于庞大
- **分析**：作为第二大 Skill，它内联了 5+ 个阶段的具体实现。不是"编排"而是"重新实现"。
- **建议**：
  - **重构为元编排 Skill**：显式调用子 Skill，压缩至 ~80 行。
  - **或转换为 Flow Skill**：`autopilot` 本质上是多阶段工作流，符合 `skills.md` 中 Flow Skill 的定义（`type: flow` + Mermaid 图）。转换为 Flow Skill 后，可用 `/flow:autopilot` 执行，各阶段作为分支节点，更符合官方对复杂多轮工作流的推荐模式。

---

## 4. 工作流低效审计（3 项）

> **官方规则依据**：`agents.md` 支持 `run_in_background=true` 并行执行；默认最大并发后台任务为 4（`interaction.md`）；`TaskList` 和 `TaskOutput` 可用于轮询后台任务。

### 4.1 `self-improve` 未并行化候选评估
- **当前逻辑**：Step 3 "对每个候选运行测试和 benchmark" 未提及 `run_in_background=true`。
- **低效点**：若 N=4 个候选，串行测试时间是并行的 4 倍。
- **优化建议**：明确添加并行评估指令：
  ```
  对每个候选启动 Agent(subagent_type="coder", description="Evaluate candidate N", prompt="...", run_in_background=true)
  所有候选启动后，使用 TaskList(active_only=true) 轮询完成状态
  全部完成后，使用 TaskOutput 收集结果并比较适应度
  ```
- **合规性**：`agents.md` 允许 `run_in_background=true`；最大并发 4，若候选数超过 4 需分批次启动。

### 4.2 `autopilot` Phase 0/1 对模糊输入的预检查不够激进
- **当前逻辑**：当输入模糊时，autopilot "提供"重定向到 `deep-interview` 或 `ralplan`，而非强制。
- **低效点**：用户若忽略建议，autopilot 会在无明确文件/函数锚点的情况下执行 Analyst + Architect 扩展，浪费 2 次顺序 Agent 调用后才可能发现问题。
- **优化建议**：将 "提供重定向" 改为 **"强制门控"**（mandatory gating）：
  > "若用户输入中未包含具体文件路径、函数名或可修改的代码锚点，必须先完成 `deep-interview` 或 `ralplan` 产出 `spec.md` 或 `plan.md`，否则不进入 Phase 1。"
- **合规性**：不违反任何规则；这是业务逻辑策略调整。

### 4.3 `team` Phase 4 "Monitor & Coordinate" 暗示串行轮询
- **当前逻辑**："跟踪每个 Agent 的完成状态"、"处理依赖阻塞"，未提及后台任务工具。
- **低效点**：若启动 4 个并行 Agent，串行等待每个完成会导致总耗时 = 最慢 Agent × 4（若顺序检查）。
- **优化建议**：添加明确的并行监控指令：
  > "使用 `TaskList(active_only=true)` 同时查询所有后台 Agent 状态，而非逐个等待。"
- **合规性**：`interaction.md` 和 `agents.md` 支持 `TaskList` 和 `TaskOutput`。

---

## 5. 合规风险审计（3 项，业务逻辑层面）

> **官方规则依据**：`agents.md` 规定 `Agent` 工具的 `description` 参数必须为 **3–5 词**；`subagent_type` 仅官方支持 `coder`、`explore`、`plan`（但项目内部扩展了更多类型，如 `architect`、`debugger` 等，需注意区分）。

### 5.1 大量 Skill 的 `Agent` 示例缺少 `description` 参数
- **影响范围**：`ralplan`, `plan`, `autopilot`, `ralph`, `team`, `external-context`, `ccg` 等 Skill 中的 `Agent(...)` Markdown 示例均未包含 `description`。
- **风险**：若 AI 严格遵循示例，可能 omission `description`，导致运行时自动生成不符合 3–5 词约束的描述，或触发 schema 校验警告。
- **优化建议**：审计并补全所有 `Agent` 示例：
  ```markdown
  Agent(
    subagent_type="plan",
    description="Create implementation plan",
    prompt="You are the Planner..."
  )
  ```
- **工作量**：约 15–20 处示例需要补全。

### 5.2 多个 Skill 滥用 `coder` 代替专用 `subagent_type`
- **影响范围**：
  - `autopilot` Phase 4 使用 `subagent_type="coder"` + prompt 注入来扮演 Architect Reviewer、Security Reviewer、Code Reviewer。
  - `ralph` Step 7 使用 `subagent_type="coder"` 执行验证。
  - `team` Phase 5 使用 `subagent_type="coder"` 执行验证。
- **反模式**：项目 Agent 目录中已定义 `architect`、`security-reviewer`、`code-reviewer`、`verifier` 等专用类型，它们拥有针对性的工具策略和系统提示。使用 `coder` + prompt 注入等于绕过这些优化配置。
- **优化建议**：
  - `autopilot` Phase 4：`architect` → `subagent_type="architect"`，`security reviewer` → `subagent_type="security-reviewer"`，`code reviewer` → `subagent_type="code-reviewer"`
  - `ralph` Step 7 / `team` Phase 5：验证工作 → `subagent_type="verifier"`
- **合规性**：`agents.md` 将 `coder`, `explore`, `plan` 列为"built-in"，但项目扩展了更多类型。使用扩展类型不违反规则，反而是对 Agent 目录的正确利用。

### 5.3 `ralph` 的 `run_in_background` 语法错误
- **位置**：`ralph/SKILL.md` 第 91 行附近
- **问题**：正文写 `run_in_background: true`（JSON/YAML 语法），而 Kimi CLI `Agent` 工具的实际参数语法是 Python 风格关键字参数 `run_in_background=true`。
- **风险**： prose 中的语法错误可能误导 AI 生成无效的 tool call。
- **优化建议**：统一修正为 `` `run_in_background=true` ``。

---

## 6. 缺失 Skill 识别（4 项）

> **官方规则依据**：无强制要求每个 Agent 必须有对应 Skill；但从业务逻辑完整性角度，专用 Agent 若无 Skill 入口，用户无法通过自然语言触发其工作流。

### 6.1 `code-reviewer` / `security-reviewer` Agent 无对应 Skill
- **现状**：Agent 目录中存在 `code-reviewer.yaml` 和 `security-reviewer.yaml`，但 Skill 目录中无对应入口。
- **用户场景**："帮我做一次代码审查"、"检查这段代码的安全问题" —— 没有自然语言触发词可直接命中。
- **建议**：
  - 创建 `skills/code-review/SKILL.md`：触发词 `code review`, `review code`, `pr review`；工作流为 `explore`（范围确定）→ `code-reviewer`（审查）→ `architect`（设计影响评估，可选）。
  - 创建 `skills/security-review/SKILL.md`：触发词 `security review`, `audit security`, `check vulnerabilities`；工作流为 `explore`（攻击面）→ `security-reviewer`（审计）→ `code-reviewer`（修复验证）。

### 6.2 无 `refactor` 专用 Skill
- **现状**：重构是介于"单文件修复"和"全项目 autopilot"之间的高频需求。当前无 dedicated Skill。
- `ai-slop-cleaner` 聚焦代码清理（删除死代码、简化），不覆盖架构级重构（提取模块、改接口、迁移模式）。
- **建议**：创建 `skills/refactor/SKILL.md`：触发词 `refactor`, `restructure`, `redesign`；工作流为 `explore`（影响分析）→ `architect`（新设计）→ `team`（并行文件修改）→ `verify`（回归验证）。

### 6.3 `omk-teams` 已废弃但仍占用 namespace
- **现状**：`omk-teams/SKILL.md` 明确自我声明为废弃，引导用户使用 `team`。它无任何独特工作流，仅提供迁移说明。
- **建议**：删除。迁移说明可并入 `team/SKILL.md` 的 "从 OMC/omk-teams 迁移" 章节。

### 6.4 `omk-reference` 是目录而非工作流
- **现状**：`omk-reference` 是一个工具/Agent 速查表（`user-invocable: false`），不面向终端用户。它更像内部文档。
- **建议**：保留但明确其定位为内部 reference，不纳入用户-facing Skill 计数。或迁移到 `docs/` 目录。

---

## 7. 优化优先级矩阵

| 优先级 | 事项 | 类型 | 涉及 Skill | 预期收益 |
|--------|------|------|-----------|----------|
| **P0** | 移除灾难级触发词 | 触发词 | `autopilot`, `ultrawork`, `cancel`, `ask`, `plan` | 消除日常对话误触，提升交互体验 |
| **P0** | 删除 `ralplan`（并入 `plan`） | 冗余 | `ralplan` → `plan` | 减少 173 行维护负债，消除漂移 |
| **P1** | 重构 `autopilot` 为元编排 | 冗余 | `autopilot` | 消除 5+ 个工作流的内联复制，减少 ~80 行 |
| **P1** | 删除 `omk-teams`、`hud` | 废弃 | `omk-teams`, `hud` | 清理 namespace，减少认知负担 |
| **P1** | 合并 `learner` → `skillify` | 冗余 | `learner`, `skillify` | 统一入口，减少重复 Skill |
| **P1** | 合并 `verify` → `ultraqa` | 粒度 | `verify`, `ultraqa` | 消除 6 处内联清单复制 |
| **P2** | 删除 `deep-dive`（并入 `trace`） | 冗余 | `deep-dive`, `trace` | 清理 trivial wrapper |
| **P2** | 补全所有 `Agent` 示例的 `description` | 合规 | 8+ 个 Skill | 避免 schema 校验问题 |
| **P2** | 使用专用 `subagent_type` | 合规/效率 | `autopilot`, `ralph`, `team` | 发挥 Agent 目录的专业化配置 |
| **P2** | 并行化 `self-improve` 评估 | 低效 | `self-improve` | 缩短进化算法评估时间 |
| **P2** | 扩展或降级 `self-improve` | 粒度 | `self-improve` | 避免模糊指令导致的高成本失控 |
| **P3** | 创建 `code-review` / `security-review` | 缺口 | 新建 2 个 Skill | 补齐 Agent 目录的自然语言入口 |
| **P3** | 创建 `refactor` Skill | 缺口 | 新建 1 个 Skill | 覆盖高频重构工作流 |
| **P3** | 澄清 `wiki`↔`remember` 边界 | 边界 | `wiki`, `remember` | 减少用户困惑 |

---

## 8. 官方业务逻辑设计约束速查

> 以下约束直接决定 Skill 工作流设计的上限，所有优化建议均在此框架内。

### Agent / 子代理
- **禁止嵌套**：Subagent 内部不能调用 `Agent`，`Agent` 仅在 Root Agent 可用（`agents.md`）。
- **描述长度**：`Agent` 的 `description` 必须 **3–5 词**（`agents.md`）。
- **超时范围**：`Agent` 的 `timeout` 必须 **30–3600 秒**（`agents.md`）。
- **内置类型**：官方仅内置 `coder`（可写）、`explore`（只读）、`plan`（只读，无 Shell）（`agents.md`）。

### Plan 模式
- **只读限制**：Plan 模式下只能用 `Glob`, `Grep`, `ReadFile`, `ReadMediaFile`, `SearchWeb`, `FetchURL`（`interaction.md`）。
- **不可用工具**：Plan 模式下**禁止** `TaskStop`（`agents.md`）。
- **退出审批**：YOLO 自动批准进入 Plan 模式，但**退出 Plan 模式仍需用户审批**；AFK/Print 模式才自动批准退出（`interaction.md`）。
- **选项限制**：`ExitPlanMode` 的 `options` 最多 3 个，标签不能是 "Approve"/"Reject"/"Revise"（`agents.md`）。

### 后台任务
- **并发上限**：默认最多 **4** 个并发后台任务（`interaction.md`）。
- **超时默认**：后台 `Agent` 默认超时 **15 分钟**（900 秒）（`agents.md`）。
- **退出即杀**：CLI 退出时，后台任务**默认被终止**（`interaction.md`）。

### 交互模式
- **YOLO**：跳过所有审批，但**仍可能弹出 `AskUserQuestion`**（`interaction.md`）。
- **AFK/Print**：跳过所有审批，**并自动忽略 `AskUserQuestion`**（`interaction.md`）。
- **提问限制**：`AskUserQuestion` 每次最多 **4 个问题**，每题最多 **4 个选项**（自动加 Other），标签 **1–5 词**（`agents.md`）。
- **不宜滥用**：`AskUserQuestion` 仅在用户选择真正影响后续操作时才调用（`agents.md`）。

### 工具限制
- **文件写入**：`WriteFile` / `StrReplaceFile` **每次都需要用户审批**（`agents.md`）。
- **Shell 执行**：**每次都需要用户审批**（`agents.md`）。
- **Glob**：**拒绝 `**` 开头**的模式；最多返回 **1000** 条（`agents.md`）。
- **ReadFile**：每次最多 **1000 行**，每行最多 **2000 字符**（`agents.md`）。

### Skill 规范
- **Flow Skill**：必须声明 `type: flow`，包含 Mermaid/D2 图，图中有且仅有 **1 个 BEGIN 和 1 个 END**（`skills.md`）。
- **行数建议**：`SKILL.md` 建议 **< 500 行**（`skills.md`）。
- **名称格式**：`name` 1–64 字符，仅限小写字母、数字、连字符（`skills.md`）。
- **调用方式**：`/skill:<name>` 加载内容；`/flow:<name>` 执行 Flow Skill 工作流（`skills.md`, `slash-commands.md`）。

---

*本报告为业务逻辑专项审计，与《OMK-Optimization-Audit-Report.md》（格式/代码/Git 审计）互为补充。*
