# OMK 文档接口契约

> 本文档为 OMK（Oh-My-Kimi）四份中文技术文档的接口契约，约束 `01-requirements.md`、`02-architecture.md`、`03-system-design.md`、`04-functional-design.md` 的内容边界、术语一致性与引用规范。
>
> 最后更新：基于 Kimi CLI `1.36.0` 规范，OMK `0.1.0`。

---

## 1. 术语表（Glossary）

以下术语映射全部提取自 `kimi-cli-docs/AGENTS.md` 的术语表，并补充 OMK 项目专用术语。所有术语在正文中出现时须使用下表规定的「中文」或 `English` 形式，以便自动化脚本检查一致性。

### 1.1 Kimi CLI 通用术语

| 中文 | English | 专有名词（zh） | 专有名词（en） |
|------|---------|---------------|---------------|
| `Agent` | `agent` | 是 | 否 |
| `Shell` | `shell` | 是 | 否 |
| `Shell 模式` | `shell mode` | 是 | 否 |
| `Print 模式` | `print mode` | 是 | 否 |
| `Wire 模式` | `Wire mode` | 是 | 是（Wire） |
| `Thinking 模式` | `thinking mode` | 是 | 否 |
| `MCP` | `MCP` | 是 | 是 |
| `ACP` | `ACP` | 是 | 是 |
| `Kimi Code CLI` | `Kimi Code CLI` | 是 | 是 |
| `Agent Skills` | `Agent Skills` | 是 | 是 |
| `Skill` | `skill` | 是 | 否 |
| `系统提示词` | `system prompt` | 否 | 否 |
| `提示词` | `prompt` | 否 | 否 |
| `会话` | `session` | 否 | 否 |
| `上下文` | `context` | 否 | 否 |
| `子 Agent` | `subagent` | 是（Agent） | 否 |
| `API 密钥` | `API key` | 是 | 否 |
| `JSON` | `JSON` | 是 | 是 |
| `JSONL` | `JSONL` | 是 | 是 |
| `OAuth` | `OAuth` | 是 | 是 |
| `macOS` | `macOS` | 是 | 是 |
| `uv` | `uv` | 是 | 是 |
| `审批请求` | `approval request` | 否 | 否 |
| `斜杠命令` | `slash command` | 否 | 否 |
| `工具调用` | `tool call` | 否 | 否 |
| `Frontmatter` | `frontmatter` | 是 | 否 |
| `User 消息` | `user message` | 是（User） | 否 |
| `Assistant 消息` | `assistant message` | 是（Assistant） | 否 |
| `Tool 消息` | `tool message` | 是（Tool） | 否 |
| `轮次` | `turn` | 否 | 否 |
| `供应商` | `provider` | 否 | 否 |
| `Prompt Flow` | `Prompt Flow` | 是 | 是 |
| `Ralph 循环` | `Ralph Loop` | 是 | 是 |
| `Diff` | `diff` | 是 | 否 |

### 1.2 JetBrains IDE 术语

| English | 中文 |
|---------|------|
| `AI Chat` | `AI 聊天` |
| `Registry` | `注册表` |

### 1.3 OMK 项目专用术语

| 中文 | English | 说明 |
|------|---------|------|
| `OMK` | `OMK` | Oh-My-Kimi 的缩写，项目代号 |
| `Kimi 编排与多智能体协调` | `Kimi Orchestration & Multi-agent Coordination` | OMK 全称 |
| `根 Agent` | `root agent` | 通过 `--agent-file` 加载的自定义顶层 Agent |
| `内置 Skills` | `built-in skills` | Kimi CLI 随包安装的基础 Skill |
| `用户级 Skills` | `user-level skills` | 存放在用户主目录的 Skills |
| `项目级 Skills` | `project-level skills` | 存放在项目目录的 Skills |
| `Flow Skill` | `Flow Skill` | 内嵌 Agent Flow 流程图的特殊 Skill |
| `Skill 发现` | `skill discovery` | Kimi CLI 分层加载 Skills 的机制 |
| `工具安全边界` | `tool safety boundary` | 文件读写审批与工作区范围限制 |
| `Plan 模式` | `Plan mode` | 先规划后执行的审批模式 |
| `YOLO 模式` | `YOLO mode` | 自动审批模式 |
| `后台任务` | `background task` | 通过 `run_in_background=true` 启动的异步任务 |
| `状态目录` | `state directory` | `.omk/state/` 及其子目录 |
| `项目记忆` | `project memory` | `.omk/project-memory.json` 中的跨会话知识 |
| `记事本` | `notepad` | `.omk/notepad.md` 中的持久化笔记 |
| `知识库` | `wiki` | `.omk/wiki/` 下的 Markdown 知识库 |

---

## 2. 内容边界矩阵（Content Boundary Matrix）

下表定义四份文档对六大关注点的「Canonical（规范源）」归属。标记为 **C** 的文档是该关注点的唯一规范源，其他文档仅允许交叉引用，不得重复定义。"允许局部展开" 列标记为 `Y` 时，表示非规范源文档可在相关章节中以不超过 3 段的篇幅做局部展开；标记为 `N` 时，仅允许一句概括性说明。

| 关注点 | 需求文档（REQ） | 架构文档（ARCH） | 系统设计（SYS） | 功能设计（FUNC） | 允许局部展开 |
|--------|---------------|-----------------|---------------|-----------------|-------------|
| `Agent YAML Schema` | 引用 | 引用 | **C** | 引用 | N |
| `状态 Schema` | 引用 | 引用 | **C** | 引用 | N |
| `CLI 命令矩阵` | **C** | 引用 | 引用 | 引用 | Y |
| `Skill/Agent 接口签名` | 引用 | **C** | 引用 | 引用 | Y |
| `配置项清单` | 引用 | 引用 | **C** | 引用 | N |
| `错误码体系` | **C** | 引用 | 引用 | 引用 | Y |
| `工具安全边界与审批机制` | 引用 | 引用 | **C** | 引用 | N |
| `通知集成协议` | 引用 | 引用 | 引用 | **C** | N |

### 边界说明

1. **Agent YAML Schema**：规范源为 `03-system-design.md`。须覆盖 `version`、`agent`、`name`、`system_prompt_path`、`system_prompt_args`、`tools`、`exclude_tools`、`subagents` 等字段，以及 `extend` 继承机制。`agents/default/agent.yaml` 的 18 个子 Agent 定义属于实例数据，不在 Schema 层面重复罗列。

2. **状态 Schema**：规范源为 `03-system-design.md`。须定义 `.omk/state/<mode>-state.json` 的 JSON Schema、`.omk/project-memory.json` 的键值约定，以及 `.omk/notepad.md` 的 Markdown 格式约定。

3. **CLI 命令矩阵**：规范源为 `01-requirements.md`。须覆盖 `kimi --agent-file`、`omk state`、`omk notifier`、`omk updater` 等命令的功能需求与参数矩阵。安装脚本 `install.sh` / `uninstall.sh` 的选项也属于需求范畴。

4. **Skill/Agent 接口签名**：规范源为 `02-architecture.md`。须说明 `Agent(subagent_type="...", prompt="...")` 的调用契约、Skill 触发词与 `SKILL.md` Frontmatter 的元数据契约，以及 Flow Skill 的 `BEGIN`/`END` 节点协议。

5. **配置项清单**：规范源为 `03-system-design.md`。须覆盖环境变量（`OMK_STATE_DIR`、`OMK_TELEGRAM_TOKEN`、`OMK_TELEGRAM_CHAT`、`OMK_DISCORD_WEBHOOK`、`OMK_SLACK_WEBHOOK`）与 `system_prompt_args` 自定义参数。

6. **错误码体系**：规范源为 `01-requirements.md`。须定义 OMK CLI 退出码（成功 `0`、参数错误 `1`、状态不存在 `2` 等）以及 Skill 执行失败时的状态回写规范。

7. **工具安全边界与审批机制**：规范源为 `03-system-design.md`。须覆盖 Shell/文件写入/MCP/后台任务停止的审批要求，以及工作区外文件的绝对路径约束。

8. **通知集成协议**：规范源为 `04-functional-design.md`。须覆盖 Telegram Bot API、Discord Webhook、Slack Webhook 的消息格式、重试策略与错误处理流程。

---

## 3. 事实清单（Fact List）

以下事实为项目客观数据，所有文档引用时须与此清单保持一致。若事实发生变更，须同步更新本契约。

| 序号 | 事实项 | 值/路径 | 来源 |
|------|--------|---------|------|
| 1 | OMK 版本 | `0.1.0` | `pyproject.toml` 的 `project.version` |
| 2 | Skills 数量与位置 | 36 个，位于 `skills/<name>/SKILL.md` | `README_ZH.md` |
| 3 | 公开 Agent 数量与位置 | 18 个，位于 `agents/default/<name>.yaml` | `agents/default/agent.yaml` 的 `subagents` |
| 4 | Python 包位置 | `omk/` 目录 | `pyproject.toml` |
| 5 | 核心 Python 模块 | `omk/state.py`、`omk/cli.py`、`omk/notifier.py`、`omk/updater.py` | `README_ZH.md` |
| 6 | Shell 脚本位置 | `scripts/` | `README_ZH.md` |
| 7 | 运行时状态目录 | `.omk/` | `README_ZH.md` |
| 8 | 状态文件子目录 | `.omk/state/` | `omk/state.py` 的 `DEFAULT_STATE_DIR` |
| 9 | 记事本文件 | `.omk/notepad.md` | `README_ZH.md` |
| 10 | 项目记忆文件 | `.omk/project-memory.json` | `README_ZH.md` |
| 11 | 规划文档目录 | `.omk/plans/` | `README_ZH.md` |
| 12 | 知识库目录 | `.omk/wiki/` | `README_ZH.md` |
| 13 | 审计日志目录 | `.omk/logs/` | `README_ZH.md` |
| 14 | 会话跟踪目录 | `.omk/state/sessions/` | `README_ZH.md` |
| 15 | Kimi CLI 兼容性目标 | `1.36.0` | `README_ZH.md` |
| 16 | 安装脚本 | `install.sh` | 项目根目录 |
| 17 | 卸载脚本 | `uninstall.sh` | 项目根目录 |
| 18 | 入口命令 | `omk`（由 `omk.cli:main` 提供） | `pyproject.toml` 的 `project.scripts` |
| 19 | 根 Agent 文件 | `agents/default/agent.yaml` | `README_ZH.md` |
| 20 | Python 最低版本 | `>=3.9` | `pyproject.toml` 的 `requires-python` |
| 21 | 许可证 | MIT | `pyproject.toml` |
| 22 | 18 个公开 Agent 名单 | `coder`、`explore`、`plan`、`architect`、`executor`、`debugger`、`critic`、`analyst`、`designer`、`writer`、`verifier`、`tracer`、`code-reviewer`、`security-reviewer`、`test-engineer`、`document-specialist`、`code-simplifier`、`scientist` | `agents/default/agent.yaml` |

---

## 4. 引用规范（Citation Rules）

### 4.1 允许的引用格式

- **章节引用**：使用 `文件路径` 的 `章节标题` / `配置项名`。
  - 示例：`kimi-cli-docs/zh/customization/agents.md` 的 `系统提示词内置参数` / `${KIMI_SKILLS}`
  - 示例：`agents/default/agent.yaml` 的 `subagents` / `coder`
- **内联文件路径**：使用反引号包裹的文件路径。
  - 示例：`omk/state.py` 中的 `get_state_dir()` 函数
  - 示例：`skills/autopilot/SKILL.md`
- **配置项名**：使用反引号包裹的 TOML/YAML/JSON 键名。
  - 示例：`pyproject.toml` 中的 `project.version`
  - 示例：`agent.yaml` 中的 `system_prompt_args`

### 4.2 禁止的引用格式

- **裸行号引用**：禁止出现 `L123`、`第 123 行`、`line 123` 等行号引用。若必须指向具体实现，应使用函数名、类名或配置项名替代。
  - ✗ `omk/state.py` 第 30 行
  - ✓ `omk/state.py` 的 `DEFAULT_STATE_DIR`
- **未经反引号包裹的术语**：禁止在正文中裸写英文术语或文件路径。
  - ✗ Agent YAML 的 extend 字段
  - ✓ `Agent` YAML 的 `extend` 字段

### 4.3 文档头部 Commit Hash 锁定

每份文档须在头部 YAML Frontmatter 或注释区中包含 `omk-commit` 字段，锁定该文档最后一次对齐检查时使用的 Git commit hash：

```markdown
---
omk-commit: <full-commit-hash>
---
```

当事实清单中的客观数据发生变更时，须同时：
1. 更新 `DOC_CONTRACT.md` 中的事实清单；
2. 重新生成受影响文档的 `omk-commit`；
3. 运行 `scripts/check-agent-contract.py` 验证文档、注册表、安装器消息和技能引用的一致性。

---

## 附录：文档清单

| 文档编号 | 文件名 | 说明 |
|----------|--------|------|
| 01 | `01-requirements.md` | 需求规格说明书（Requirements Specification） |
| 02 | `02-architecture.md` | 总体架构文档（Overall Architecture Document） |
| 03 | `03-system-design.md` | 系统设计文档（System Design Document） |
| 04 | `04-functional-design.md` | 功能设计文档（Functional Design Document） |
