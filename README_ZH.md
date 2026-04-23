# OMK（Kimi 编排与多智能体协调）

> Oh-My-Kimi。为 [Kimi Code CLI](https://github.com/MoonshotAI/kimi-cli) 打造的多智能体编排系统。35+ 工作流技能，18 个公开专家智能体，以及有状态执行。

## 概述

OMK 将完整的 OMC 多智能体编排体验移植到 Kimi CLI。它提供：

- **36 个工作流技能** — autopilot、ralph、ultrawork、team、plan、deep-dive 等
- **18 个公开专家智能体** — coder、plan、architect、executor、debugger、critic、verifier 等
- **统一的状态管理** — 持久化计划、记事本、项目记忆和知识库
- **通知集成** — 通过 shell 脚本支持 Telegram、Discord、Slack
- **零 Claude 依赖** — 完全基于 Kimi CLI 原生工具集运行

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/oh-my-kimi.git
cd oh-my-kimi

# 2. 全局安装技能和 omk CLI（默认：~/.kimi/skills/ + pip install -e .）
./install.sh

# 3. 或项目本地安装
./install.sh --project

# 4. 或安装到指定项目
./install.sh --target-dir ~/my-project

# 5. 或仅安装技能（跳过 omk Python 包）
./install.sh --no-pip

# 6. 在 Kimi CLI 上启动 OMK
# 注意：以下路径在执行 ./install.sh 后才会生成
# 全局安装（当 XDG_CONFIG_HOME 未设置时的默认行为）
kimi --agent-file "$HOME/.kimi/agents/agent.yaml"

# 如果 XDG_CONFIG_HOME 已设置
kimi --agent-file "$XDG_CONFIG_HOME/kimi/agents/agent.yaml"

# 项目本地安装（从项目根目录运行）
kimi --agent-file ./.kimi/agents/agent.yaml

# 7. 验证 omk CLI 是否全局可用
omk --help
omk state list
```

### 安装选项

| 选项 | 说明 |
|------|------|
| `--project` | 安装到 `./.kimi/skills/`（项目本地） |
| `--target-dir DIR` | 安装到 `DIR/.kimi/skills/` |
| `--force` | 覆盖现有技能 |
| `--dry-run` | 预览将要安装的内容 |
| `--no-pip` | 跳过全局安装 `omk` Python 包 |
| `--help` | 显示完整帮助 |

### 兼容性目标

OMK 支持的 Kimi CLI `1.36.0` 引导契约如下：

- 将技能安装到 Kimi 可识别的技能目录，例如 `~/.kimi/skills/` 或 `./.kimi/skills/`。
- 通过 `--agent-file` 启动带有 OMK 自定义根智能体的 Kimi。
- 将不带 `--agent-file` 的纯 `kimi` 命令视为普通 Kimi，而非 OMK。

### 首次使用

使用 OMK 根智能体启动 Kimi，然后通过关键词自然调用技能：

```bash
kimi --agent-file ./.kimi/agents/agent.yaml

autopilot: build a REST API for user management
ralph: refactor the auth module until all tests pass
plan this feature with consensus mode
team 3:executor fix all TypeScript errors
deep dive into why the build is failing
ultraqa the login flow
```

## 卸载

```bash
# 移除 OMK 技能、智能体配置和 omk Python 包
./uninstall.sh

# 项目本地卸载
./uninstall.sh --project

# 从指定项目卸载
./uninstall.sh --target-dir ~/my-project

# 预览将要移除的内容（不实际删除）
./uninstall.sh --dry-run

# 跳过确认提示
./uninstall.sh --force

# 保留 .omk/ 运行时状态目录
./uninstall.sh --keep-state
```

### 卸载选项

| 选项 | 说明 |
|------|------|
| `--project` | 从 `./.kimi/skills/` 卸载（项目本地） |
| `--target-dir DIR` | 从 `DIR/.kimi/skills/` 卸载 |
| `--keep-state` | 保留 `.omk/` 运行时状态目录 |
| `--force` | 跳过确认提示 |
| `--dry-run` | 预览将要移除的内容 |
| `--help` | 显示完整帮助 |

## 架构

```
User Input → kimi --agent-file .kimi/agents/agent.yaml → Skill Detection → Agent Orchestration → Tools & State
                                                           │                    │
                                                           ▼                    ▼
                                                    .kimi/skills/         Agent YAML configs
                                                    (35+ SKILL.md)        (18 public roles)
                                                           │                    │
                                                           └────────┬───────────┘
                                                                    ▼
                                                             .omk/state/
                                                         (JSON/Markdown files)
```

## 核心技能

### 工作流技能

| 技能 | 触发词 | 说明 |
|------|--------|------|
| `autopilot` | "autopilot", "build me", "I want a" | 从想法到可运行代码的全自主执行 |
| `ralph` | "ralph", "don't stop", "must complete" | 自引用持久循环，基于 PRD 驱动验证 |
| `ultrawork` | "ultrawork", "ulw", "parallel" | 通过并行智能体编排实现最大并行度 |
| `team` | "team" | N 个协调智能体共享任务列表 |
| `plan` | "plan this", "plan the", "let's plan" | 可选访谈的战略规划 |
| `ralplan` | "ralplan", "consensus plan" | 带审议的迭代共识规划 |
| `deep-interview` | "deep interview", "interview me" | 苏格拉底式深度访谈，含歧义门禁 |
| `deep-dive` | "deep dive" | 两阶段流水线：trace → deep-interview |
| `ultraqa` | "ultraqa" | QA 循环 — 测试、验证、修复、重复 |
| `ai-slop-cleaner` | "cleanup", "deslop", "anti-slop" | 回归安全清理工作流 |
| `visual-verdict` | "visual verdict" | 针对截图对比的结构化视觉 QA |
| `trace` | "trace" | 基于证据的追踪，含竞争性假设 |
| `ccg` | "ccg" | Claude-Codex-Gemini 三模型编排 |
| `sciomk` | "sciomk" | 并行科学家智能体进行全面分析 |
| `self-improve` | "self-improve" | 自主进化式代码改进 |

### 实用工具

| 技能 | 触发词 | 说明 |
|------|--------|------|
| `cancel` | "cancel", "stop", "abort" | 取消活跃的执行模式 |
| `ask` | "ask" | 提供商顾问路由（Claude、Codex、Gemini） |
| `setup` | "setup" | 安装或刷新 OMK 组件 |
| `omk-doctor` | "doctor" | 诊断安装问题 |
| `verify` | "verify" | 验证变更是否确实有效 |
| `debug` | "debug" | 诊断当前会话或仓库状态 |
| `release` | "release" | 通用发布助手 |
| `skill` | "skill" | 管理本地技能 |
| `skillify` | "skillify" | 将工作流转换为技能草稿 |
| `configure-notifications` | "configure notifications" | 配置 Telegram、Discord、Slack |
| `mcp-setup` | "mcp setup" | 配置外部 CLI 工具（ast-grep、Playwright 等） |

### 记忆与知识

| 技能 | 触发词 | 说明 |
|------|--------|------|
| `learner` | "learner" | 从对话中提取已学技能 |
| `wiki` | "wiki" | 持久化 Markdown 知识库 |
| `writer-memory` | "writer-memory" | 写作者智能体记忆 |
| `remember` | "remember" | 回顾可复用的项目知识 |
| `omk-reference` | (自动加载) | 智能体目录、工具、流水线路由 |

完整目录请见 `skills/` 目录。

## 智能体目录

通过 `Agent(subagent_type="<name>", ...)` 调用。

### 构建/分析通道

| 智能体 | 说明 | 适用场景 |
|--------|------|----------|
| `coder` | 通用软件工程任务 | 小型或混合实现工作 |
| `explore` | 快速代码库搜索、文件/符号映射 | 快速查找、定位文件、理解结构 |
| `analyst` | 需求澄清、验收标准、隐藏约束 | 宽泛请求、模糊需求 |
| `plan` | 任务排序、执行计划、风险标记 | 多文件实现前 |
| `architect` | 系统设计、边界、接口、长期权衡 | 复杂重构、新功能 |
| `debugger` | 根因分析、回归隔离、故障诊断 | 构建错误、测试失败、Bug |
| `executor` | 代码实现、重构、功能开发 | 编码任务的默认选择 |
| `verifier` | 完成度验证、声明验证、测试充分性 | 声称完成前 |
| `tracer` | 基于证据的追踪、竞争性假设 | 因果调查 |

### 审查通道

| 智能体 | 说明 | 适用场景 |
|--------|------|----------|
| `code-reviewer` | 全面审查 — 逻辑、可维护性、反模式 | 合并前质量门禁 |
| `security-reviewer` | 漏洞、信任边界、认证/授权 | 安全关键变更 |

### 领域专家

| 智能体 | 说明 | 适用场景 |
|--------|------|----------|
| `test-engineer` | 测试策略、覆盖率、脆弱测试加固 | 添加或改进测试 |
| `designer` | UI/UX 架构、交互设计 | 前端工作、样式调整 |
| `writer` | 文档、迁移说明、用户指南 | 文档任务 |
| `document-specialist` | 外部文档、API/SDK 参考查询 | 未知 SDK、框架 |
| `code-simplifier` | 代码清晰度、简化、可维护性 | 清理、去冗余 |
| `scientist` | 数据分析、统计研究 | 数据密集型任务 |

### 协调

| 智能体 | 说明 | 适用场景 |
|--------|------|----------|
| `critic` | 计划/设计批判性挑战 | 提交计划前 |

Kimi CLI `1.36.0` 的兼容性目标：上述 18 个公开 OMK 智能体名单为支持的公开接口。额外的已发布 YAML 文件除非接入到已记录的工作流，否则不属于支持的公开接口。

## OMK CLI 与状态管理

OMK 包含一个 Python 工具包（`omk/`），用于状态管理和辅助功能：

```bash
# 状态管理（全局 omk CLI 或 python3 -m）
omk state list                          # 列出活跃模式
omk state read ralph                    # 读取 ralph 状态
omk state write ralph '{"active":true}' # 写入状态
omk state clear ralph                   # 清除状态

# 通知
omk notifier telegram "Build complete"
omk notifier discord "Deployment done"

# 更新检查
omk updater

# 传统模块语法仍然可用
python3 -m omk.state list
python3 -m omk.notifier telegram "msg"
python3 -m omk.updater
```

OMK 将所有运行时状态存储在项目目录下的 `.omk/` 中：

| 路径 | 用途 |
|------|------|
| `.omk/state/` | 模式状态文件（JSON） |
| `.omk/notepad.md` | 会话持久化笔记 |
| `.omk/project-memory.json` | 跨会话项目知识 |
| `.omk/plans/` | 规划文档 |
| `.omk/wiki/` | Markdown 知识库 |
| `.omk/logs/` | 审计日志 |

## 脚本与集成

`scripts/` 目录提供基于 shell 的实用工具：

| 脚本 | 用途 |
|------|------|
| `notify.sh` | 向 Telegram、Discord、Slack 发送通知 |
| `update-check.sh` | 从 GitHub releases 检查 OMK 更新 |
| `ast-search.sh` | 通过 ast-grep 进行结构化代码搜索 |
| `lsp-diagnostics.sh` | 语言服务器诊断包装器 |
| `rate-limit-wait.sh` | 速率限制处理助手 |
| `check-agent-contract.py` | 验证注册表、文档、安装器消息和技能角色引用保持对齐 |

### 通知设置

通过环境变量配置：

```bash
export OMK_TELEGRAM_TOKEN="your-bot-token"
export OMK_TELEGRAM_CHAT="your-chat-id"
export OMK_DISCORD_WEBHOOK="your-webhook-url"
export OMK_SLACK_WEBHOOK="your-webhook-url"
```

或使用 `configure-notifications` 技能进行引导式设置。

## 扩展功能

### 项目会话管理器

管理隔离的 git worktree 以进行并行开发：

```
"project session feat-auth-123"
"worktree for issue #456"
```

会话在 `.omk/state/sessions/` 中跟踪分支和 worktree 元数据。

### 外部工具设置

OMK 可以为增强的智能体能力配置外部 CLI 工具：

| 工具 | CLI | 使用场景 |
|------|-----|----------|
| ast-grep | `sg` | 结构化代码搜索 |
| Playwright | `npx @playwright/mcp` | 浏览器自动化 |

使用 `mcp-setup` 技能来配置这些工具。

## 与 OMC 的差异

| 功能 | OMC (Claude Code) | OMK (Kimi CLI) |
|------|-------------------|----------------|
| 智能体系统 | Claude Agent SDK `Task()` | Kimi CLI `Agent()` |
| 模型路由 | haiku/sonnet/opus | 基于提示的引导 |
| 钩子 | 生命周期事件的 Shell 钩子 | 技能触发器 + AGENTS.md |
| 团队工作器 | tmux + Claude CLI 进程 | 原生 Agent 并行调用 |
| MCP 服务器 | 进程内 MCP | `mcp-setup` 技能 + 外部 CLI 包装器 |
| HUD | 标准输入状态栏 | 不支持 |
| 通知 | 钩子驱动 | Shell curl 脚本 + 环境变量 |

## 兼容性矩阵

| 启动模式 | 支持 | 说明 |
|----------|------|------|
| 纯 `kimi` | 否 | 不会加载 OMK 自定义根智能体 |
| `kimi --agent-file <installed-agent.yaml>` | 是 | Kimi CLI `1.36.0` 支持的引导路径 |
| 仅内置 Kimi 子智能体 | 部分 | 对普通 Kimi 有用，但不是 OMK 工作流接口 |
| OMK 扩展公开名单 | 是 | 通过 OMK `--agent-file` 路径启动时支持 |

## 验证

对于 Kimi CLI `1.36.0`，最低兼容性证明如下：

1. 安装 OMK。
2. 使用 `--agent-file` 启动 Kimi。
3. 使用仅限自定义的子智能体冒烟提示（如 `verifier`）证明自定义根智能体已激活。
4. 运行契约检查脚本，确认文档、安装器消息、根注册表和技能引用已对齐。

## 贡献

1. 技能位于 `skills/<name>/SKILL.md`
2. 智能体位于 `agents/default/<name>.yaml`
3. 脚本位于 `scripts/`
4. Python 工具位于 `omk/`
5. SKILL.md 格式请遵循[技能创建指南](https://moonshotai.github.io/kimi-cli/zh/customization/skills.html)

## 许可证

MIT
