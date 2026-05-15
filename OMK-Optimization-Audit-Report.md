# OMK 项目全维度优化审计报告

> **审计范围**：`oh-my-kimi` 项目（36 Skills、21 Agents、`omk/` Python 包、脚本、文档、Git 卫生）  
> **合规基线**：`kimi-cli-docs/zh/` 本地快照（20 个文件，视为权威规则集）  
> **交付形式**：仅报告，不修改代码  
> **生成日期**：2025-05-15

---

## 执行摘要（Top 5 优先事项）

| 优先级 | 事项 | 严重程度 | 影响 |
|--------|------|----------|------|
| 1 | **修复 `your-org` 占位符** | 🔴 Critical | `updater.py`、`scripts/update-check.sh`、`README.md`/`README_ZH.md` 中的 `your-org/oh-my-kimi` 会导致更新检查 404、克隆链接失效 |
| 2 | **清理已跟踪的 `__pycache__`** | 🔴 Critical | `omk/__pycache__/` 和 `scripts/__pycache__/` 被 Git 跟踪，违反 `.gitignore` 规则；`.gitignore` 中 `.scripts/__pycache__/` 的路径前缀有误（多了点） |
| 3 | **修复 `omk/cli.py` 的 `sys.argv` 篡改** | 🔴 Critical | 第 44 行直接修改 `sys.argv` 后调用 `state_cli()`，任何依赖 `sys.argv` 的下游代码都会看到伪造值，极易引发难以调试的 Bug |
| 4 | **修复 `scripts/notify.sh` 的 HTTP/JSON 安全问题** | 🔴 Critical | `curl` 未 URL 编码消息体、未加 `--fail`、Discord/Slack JSON 未转义，会导致无效 JSON、HTTP 错误被静默吞掉 |
| 5 | **补充 `omk/` 的测试覆盖** | 🟡 Warning | `omk/` 5 个 Python 模块零测试；`pyproject.toml` 未配置 pytest；建议立即建立基础测试套件 |

---

## 1. 官方文档规则合规审计

### 1.1 Skill 合规性（36/36 通过）

**结论：全部 36 个 Skill 均符合 `kimi-cli-docs/zh/customization/skills.md` 的官方规则。**

| 检查项 | 结果 | 说明 |
|--------|------|------|
| `name` 格式（1–64 字符，小写/数字/连字符） | ✅ 通过 | 所有 Skill 名称均合法 |
| `SKILL.md` 行数 ≤ 500 | ✅ 通过 | 最大为 `team`（199 行） |
| `description` 存在性 | ✅ 通过 | 全部在 frontmatter 中声明，无 fallback |
| 相对路径使用 | ✅ 通过 | 无绝对路径引用 Skill 内部资源 |
| `Agent` 工具参数合规 | ✅ 通过 | Skill 中无具体的违规 `Agent` 调用实例 |
| `AskUserQuestion` 参数合规 | ✅ 通过 | 无具体的违规调用实例 |
| `ExitPlanMode` 禁用标签 | ✅ 通过 | 无 "Approve"/"Reject"/"Revise" 标签误用 |
| Flow Skill 规范 | ✅ 通过 | 无 Skill 声明 `type: flow`，因此不适用 |
| `TaskStop` Plan 模式误用 | ✅ 通过 | 仅在 `omk-reference` 中作为工具目录列出，无实际调用 |
| `Glob` `**` 模式 | ✅ 通过 | 所有 `**` 均为 Markdown 粗体格式，非 glob |

### 1.2 Agent 合规性（20/21 通过，1 处轻微问题）

**结论：所有 Agent YAML 语法合法，工具列表标准，无嵌套 `Agent` 违规。仅 root registry 有一处轻微不一致。**

| 文件 | 状态 | 发现 |
|------|------|------|
| `agents/default/agent.yaml`（root registry） | ⚠️ Issue | `name: ""` 为空，与文件名 `agent.yaml` 不一致 |
| `agents/default/analyst.yaml` ~ `writer.yaml`（18 个公开 + 2 个非公开） | ✅ PASS | YAML 语法、字段、继承均合规 |

**补充说明（非违规，但值得注意）：**
- `allowed_tools` 字段：所有 subagent YAML 使用 `allowed_tools` 而非 `tools`。官方文档在 `breaking-changes.md` 中认可该字段，因此不视为违规。
- `when_to_use` 字段：所有 subagent YAML 包含此字段，官方文档未列出，但不与任何规则冲突。
- Root registry 的 `description` 平均 6–7 词：官方 `Agent` 工具参数要求 `description` 为 3–5 词。Registry 中的描述仅在运行时被用作 `description` 参数才构成违规；目前无法确认是否被直接传递，建议审核调用方。

### 1.3 工具使用规则合规（项目代码层面）

| 规则来源 | 检查项 | 结果 |
|----------|--------|------|
| `agents.md` | `omk/` 导入 Kimi CLI 内部模块 | ✅ 无导入，`omk/` 完全解耦 |
| `agents.md` | 代码中存在嵌套 `Agent` 调用 | ✅ 无 |
| `agents.md` | `Agent` 的 `timeout` 超出 30–3600 范围 | ✅ 无具体调用 |
| `agents.md` | `AskUserQuestion` 超过 4 题或选项超过 4 个 | ✅ 无具体调用 |
| `agents.md` | `ExitPlanMode` 使用禁用标签 | ✅ 无 |
| `interaction.md` | `TaskStop` 在 Plan 模式中被调用 | ✅ 无 |

---

## 2. 代码质量审计

### 2.1 `omk/` Python 包

#### `omk/updater.py`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 17 | 🔴 Critical | `REPO = "your-org/oh-my-kimi"` 占位符，实际远程为 `dorname/oh-my-kimi`，导致更新检查 404 | 替换为 `"dorname/oh-my-kimi"` |
| 16 | 🟡 Warning | `CURRENT_VERSION = "0.1.0"` 硬编码且与项目成熟度不符 | 从 `pyproject.toml` 或 `omk/__init__.py` 单一来源读取版本 |
| 25 | 🟡 Warning | `urllib.request.urlopen` 无 HTTP 错误处理，403/404/网络异常直接抛未处理异常 | 包 `try/except urllib.error.HTTPError` |
| 25 | 🟡 Warning | 未处理 GitHub API 限流头 `X-RateLimit-Remaining` | 检查响应头并在限流时发出警告 |
| 27 | 🟡 Warning | 盲目假设 `tag_name` 存在且格式正确，空值被当作"无更新" | 显式验证 `tag_name` 存在且非空 |
| 30 | 🟡 Warning | 裸 `except Exception` 会吞掉 `KeyboardInterrupt` 和 `SystemExit` | 收窄为 `(urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError)` |

#### `omk/notifier.py`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 20 | 🟡 Warning | `get_script_dir()` 假设 `scripts/` 与 `omk/` 同级，pip 安装后该目录不存在 | 将 `notify.sh` 作为包数据打包，或用原生 Python 实现通知逻辑 |
| 26 | 🔵 Info | 错误信息打印到 stdout 而非 stderr | 改用 `print(..., file=sys.stderr)` |
| 30–35 | 🟡 Warning | `subprocess.run` 无 `timeout`，若 `notify.sh` 网络阻塞会永远挂起 | 添加 `timeout=30` |
| 41 | 🟡 Warning | 裸 `except Exception` 吞掉 `KeyboardInterrupt`/`SystemExit` | 收窄为 `subprocess.SubprocessError` 或 `OSError` |

#### `omk/cli.py`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 44 | 🔴 Critical | 在调用 `state_cli()` 前直接篡改 `sys.argv`，任何下游代码检查 `sys.argv` 都会看到伪造值 | 重构 `state.py` 接受显式参数（如 `state_cli(action, mode, data)`） |
| 55 | 🔵 Info | 无子命令时返回退出码 `0`，不符合 CLI 惯例 | 无子命令时返回 `2` |

#### `omk/state.py`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 10 | 🔵 Info | 文档字符串拼写错误：`write_state('ralph', {...)}` 括号不匹配 | 修正为 `write_state('ralph', {...})` |
| 63 | 🟡 Warning | 原子写入使用固定临时后缀 `.tmp`，并发写入会竞争同一临时文件名 | 使用 `tempfile.NamedTemporaryFile(dir=path.parent, delete=False)` 保证唯一性 |
| 67–68 | 🔵 Info | `os.fsync(f.fileno())` 只 fsync 文件，未 fsync 父目录，崩溃时目录项可能未持久化 | `replace()` 后打开父目录并执行 `os.fsync()`（POSIX 最佳实践） |
| 70 | 🟡 Warning | 写入路径的裸 `except Exception` 会吞掉 `KeyboardInterrupt` | 收窄为 `OSError`，或至少排除 `KeyboardInterrupt` |
| 91–97 | 🟡 Warning | `list_states()` 对匹配文件剥去 `-state` 后缀，但对不匹配文件返回原始文件名，导致名称冲突（如 `foo.json` 和 `foo-state.json` 都映射为 `foo`） | 统一行为：要么跳过无 `-state` 后缀的文件，要么始终返回原始 stem |
| 45–54 | 🟡 Warning | `read_state()` 对任何 JSON 解码错误或 OS 错误静默返回 `None`，掩盖文件损坏 | 将具体错误记录到 stderr，或抛出自定义异常让调用方区分"缺失"与"损坏" |

#### `omk/__init__.py`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 8 | 🟡 Warning | `__version__ = "0.1.0"` 与项目成熟度不匹配，且与 `pyproject.toml` 硬编码重复 | 从 `pyproject.toml` 单一来源读取版本 |

### 2.2 Shell 脚本

#### `scripts/notify.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 25–28 | 🔴 Critical | `curl -d "text=${msg}"` 未 URL 编码，`&`、`=`、`%` 等特殊字符会破坏 POST 正文 | 使用 `curl --data-urlencode` |
| 25 | 🟡 Warning | `curl` 无超时，网络阻塞会无限挂起 | 添加 `--max-time 10 --connect-timeout 5` |
| 25–28, 38–40, 50–52 | 🔴 Critical | `curl` 缺少 `-f`/`--fail`，HTTP 4xx/5xx 仍返回退出码 0，错误被静默吞掉 | 所有 `curl` 调用添加 `--fail` 或 `--fail-with-body` |
| 38–40, 50–52 | 🔴 Critical | Discord/Slack JSON 载荷使用原始字符串插值，无 JSON 转义，引号和换行会产生无效 JSON | 使用 `jq` 或 Python 单行脚本安全构造 JSON |

#### `scripts/update-check.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 12 | 🔴 Critical | `REPO="your-org/oh-my-kimi"` 占位符导致 404 | 替换为 `"dorname/oh-my-kimi"` |
| 13 | 🟡 Warning | `CURRENT_VERSION="0.1.0"` 硬编码 | 从 `omk/__init__.py` 或 `pyproject.toml` 单一来源读取 |
| 26 | 🟡 Warning | `grep | sed` 解析 JSON 极脆弱，GitHub API 空格变化即可破坏 | 使用 `python3 -c "import json,sys; ..."` 或 `jq` |
| 26 | 🟡 Warning | `curl -s` 无 `-f`，HTTP 错误被隐藏 | 添加 `--fail --max-time 10` |

#### `scripts/ast-search.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 47–65 | 🔴 Critical | 参数解析直接访问 `$2` 但未检查存在性，在 `set -u` 下 `--search` 作为最后一个参数会触发未绑定变量致命错误 | 每次访问 `$2` 前加 `if [[ -z "${2:-}" ]]; then ...; fi` 保护 |
| 116 | 🔵 Info | `echo "Running: $SG_CMD ${ARGS[*]}"` 显示数组时使用了 `[*]` | 对显示目的而言可接受，`[@]` 更安全 |

#### `scripts/rate-limit-wait.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 13–14 | 🟡 Warning | 硬编码相对路径 `.omk/...`，假设 CWD 为项目根目录，在其他目录运行会创建散目录 | 基于 `SCRIPT_DIR` 计算绝对路径，或验证 CWD |
| 23–30 | 🟡 Warning | Daemon 主体为空操作占位符（仅 `sleep 30` 循环），脚本宣称的功能未实现 | 实现实际日志监控，或添加显式 TODO/报错退出 |
| 32 | 🔵 Info | `echo $! > "$PIDFILE"` 中 `$!` 未引号 | 统一风格：`echo "$!" > "$PIDFILE"` |
| — | 🟡 Warning | 无 `trap` 清理 PID 文件，异常终止（kill -9、断电）会留下僵尸 PID 文件 | 在 daemon 子 shell 中添加 `trap 'rm -f "$PIDFILE"; exit' EXIT` |

#### `scripts/smoke-test.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 52 | 🟡 Warning | `python3 -c "import yaml; yaml.safe_load(open('$f'))"` 将文件路径直接插值到单引号 Python 字符串中，路径含 `'` 会崩 | 使用 `python3 -c '...' -- "$f"` 或通过 stdin 传入路径 |
| 52 | 🔵 Info | `open('$f')` 泄漏文件描述符（未关闭） | 使用 `with open(...) as fh:` |
| 109 | 🟡 Warning | `for f in "$SKILLS_DIR"/*/SKILL.md; do` 在目录为空时会将字面 glob 字符串当作一次迭代 | 添加 `shopt -s nullglob` 或在循环前用 `[[ -d "$SKILLS_DIR" ]]` 保护 |

#### `install.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 155 | 🟡 Warning | `((count++))` 是 bash 特有语法，与 `uninstall.sh` 使用的 POSIX `$((count + 1))` 不一致 | 统一为 `$((count = count + 1))` |
| 262 | 🟡 Warning | `install_cmd="... '$SCRIPT_DIR'"` 构造 shell 命令字符串后用 `eval` 执行，若 `$SCRIPT_DIR` 含单引号会失败 | 使用数组 `cmd=(pip install -q -e "$SCRIPT_DIR")` 并直接执行 |
| 141 | 🔵 Info | `echo "$(dirname "$target_dir")/agents"` 多余地包裹 `dirname` | 简化为 `dirname "$target_dir"` 后追加 `/agents` |
| 13 | 🔵 Info | 使用 `#!/usr/bin/env bash` + `pipefail` + bash 数组，非 POSIX `sh` | 添加注释确认 bash ≥4 要求（信息级，非问题） |

#### `uninstall.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 232 | 🔵 Info | `uv pip show omk &>/dev/null 2>&1` 中 stderr 重定向在 `&>/dev/null` 后冗余 | 删除 `2>&1` |
| 224 | 🟡 Warning | `pip_cmd show omk` 可能在 `pip3` 缺失时调用 Python 2 的 `pip` | 优先使用 `python3 -m pip` 或验证 `pip --version` |

#### `cleanup-legacy.sh`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 82 | 🟡 Warning | `npm_global_bin="$(npm prefix -g 2>/dev/null)/bin" || true` 在 `npm prefix -g` 失败时结果为 `/bin`，导致后续错误匹配 `/bin/omk` | 单独检查 `npm prefix` 的退出码，成功后再拼接 `/bin` |

### 2.3 `scripts/check-agent-contract.py`

| 行 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| 140 | 🟡 Warning | `LEGAL_SUBAGENT_TYPES = {"coder", "explore", "plan"}` 仅硬编码 3 种类型；未来引用其他合法 agent（如 `debugger`）会被错误拒绝 | 从 `PUBLIC_AGENTS` 或 registry 动态推导 |
| 237 | 🟡 Warning | `desc_match` 正则 `(?=^\w|\n---|$)` 脆弱，描述含 `---` 或以单词字符开头的行会被截断 | 先用 `\n---\n` 分割 frontmatter 与正文 |
| 338 | 🟡 Warning | `extract_skill_descriptions_from_frontmatter` 使用单行正则 `^description:\s*(.+)$`，与其自身的多行解析器逻辑不一致 | 统一使用一种稳健的解析方式（如仅解析 frontmatter 的 `yaml.safe_load`） |
| 533–540 | 🔵 Info | 对 `install.sh`/`README` 的措辞使用硬编码字符串检查，措辞微调即导致契约检查失败 | 使用正则或更宽松的子串匹配 |

---

## 3. 测试覆盖审计

| 模块/区域 | 当前状态 | 严重程度 | 说明与建议 |
|-----------|----------|----------|------------|
| `omk/__init__.py`, `omk/cli.py`, `omk/notifier.py`, `omk/state.py`, `omk/updater.py` | **零测试** | 🔴 Critical | `omk/` 5 个模块无任何测试。建议立即创建 `tests/test_omk_state.py`、`tests/test_omk_notifier.py`、`tests/test_omk_updater.py`、`tests/test_omk_cli.py`。 |
| `pyproject.toml` 测试配置 | **未配置 pytest** | 🟡 Warning | 无 `[tool.pytest.ini_options]`，无测试依赖。测试只能通过 `python3 tests/test_check_agent_contract.py` 直接运行。建议添加 pytest 配置并引入 `pytest` 依赖。 |
| `tests/test_check_agent_contract.py` | **覆盖率约 30–35%** | 🟡 Warning | 约 20 个测试函数，仅覆盖提取器 helper；未覆盖 `main()` 编排逻辑、`check_agent_yaml_structure()`、`check_skill_subagent_refs()`。建议补充集成路径测试。 |
| `scripts/check-agent-contract.py` | **未覆盖主逻辑** | 🟡 Warning | 约 200 行的 `main()` 函数无测试。建议为主流程添加冒烟测试。 |

### 推荐测试清单

| 模块 | 推荐测试用例 |
|------|--------------|
| `omk/state.py` | `get_state_dir()` 尊重 `OMK_STATE_DIR`；`write_state()` 原子写（temp + rename）；`read_state()` 对缺失文件返回 `None`，对损坏 JSON 处理；`list_states()` 正确剥去 `-state`；`is_mode_active()` / `get_active_modes()` 逻辑 |
| `omk/notifier.py` | `send_notification()` 在子进程退出 0 时返回 `True`，非零返回 `False`；`notify.sh` 缺失时优雅降级；`cli()` 拒绝未知平台 |
| `omk/updater.py` | Mock `urlopen` 测试版本比较；测试网络失败异常处理；验证 `REPO` 占位符不会破坏 URL 构造 |
| `omk/cli.py` | `argparse` 分发测试（`state`、`notifier`、`updater`）；验证必需位置参数；验证 help 输出 |

---

## 4. Git 卫生审计

| 区域 | 严重程度 | 发现 | 修复建议 |
|------|----------|------|----------|
| Tracked `__pycache__` | 🔴 Critical | `omk/__pycache__/` 和 `scripts/__pycache__/` 被 Git 跟踪（3 个 `.pyc` 文件） | 执行 `git rm -r --cached omk/__pycache__ scripts/__pycache__` |
| `.gitignore` 路径错误 | 🔴 Critical | `.gitignore` 写为 `.scripts/__pycache__/`（带前导点），实际目录是 `scripts/__pycache__/` | 修正为 `scripts/__pycache__/` |
| IDE/工具目录未忽略 | 🟡 Warning | `.vscode/`、`.specstory/`、`.cursorindexingignore` 为 untracked 且未在 `.gitignore` 中 | 加入 `.gitignore`（若不想共享）或提交（若为有意共享配置） |
| 分支不一致 | 🟡 Warning | 本地 `master` 领先 `origin/main` 11 个提交；`origin/HEAD` 指向 `origin/master`；两分支历史分叉 | 统一默认分支，删除 stale 远程分支 |
| 大二进制文件 | 🔵 Info | `kimi-cli-docs/media/acp-integration.gif` (~4.5MB)、`shell-mode.gif` (~3.5MB) 存在于历史 | 建议迁移至 Git LFS 或外部 CDN |
| 生成产物 | ✅ OK | `*.egg-info/`、`build/`、`dist/` 已正确 untracked | 无需操作 |

---

## 5. 文档与配置准确性审计

| 文件 | 行 | 严重程度 | 发现 | 修复建议 |
|------|----|----------|------|----------|
| `README.md` | ~19 | 🔴 Critical | 含占位符 `git clone https://github.com/your-org/oh-my-kimi.git` | 替换为 `https://github.com/dorname/oh-my-kimi.git` |
| `README_ZH.md` | ~19 | 🔴 Critical | 同上 | 同上 |
| `omk/updater.py` | 17 | 🔴 Critical | `REPO = "your-org/oh-my-kimi"` | 替换为 `"dorname/oh-my-kimi"` |
| `docs/` 目录 | — | 🟡 Warning | 仅 `docs/zh/` 存在，无 `docs/en/`；内容可能相对 README 陈旧 | 添加英文文档、添加索引 `docs/README.md`，或若不再维护则归档 |
| `README_ZH.md` | — | 🟡 Warning | 验证章节比 `README.md` 简略，缺少显式的 smoke-test 和 contract-check 命令 | 同步英文 README 的验证步骤到中文 README |
| `pyproject.toml` | 7 | 🟡 Warning | `version = "0.1.0"` 陈旧 | 提升版本号或引入动态版本管理 |
| `pyproject.toml` | 11 | 🔵 Info | `requires-python = ">=3.9"`，但官方文档推荐 3.12–3.14 | 收紧至 `>=3.12`（若 3.9 不再支持）或文档说明原因 |
| `pyproject.toml` | 5–18 | 🔵 Info | 缺少 `authors`、`classifiers`、显式 `dependencies = []` | 补充作者、分类器、显式空依赖列表以表明仅使用标准库 |
| `AGENTS.md` | — | 🔵 Info | 声明 18 个公开 agent，实际也为 18 个；但未提及 `git-master.yaml` 和 `qa-tester.yaml` 的存在 | 添加注释说明目录中另有 2 个非公开 agent，避免困惑 |

---

## 6. 版本一致性矩阵

当前版本号散布于多处且不一致/陈旧：

| 文件 | 当前值 | 建议 |
|------|--------|------|
| `pyproject.toml` | `0.1.0` | 单一来源 |
| `omk/__init__.py` | `0.1.0` | 从 `pyproject.toml` 读取 |
| `omk/updater.py` | `0.1.0` | 从 `pyproject.toml` 读取 |
| `scripts/update-check.sh` | `0.1.0` | 从 `omk/__init__.py` 读取 |

**建议**：在 `pyproject.toml` 中设置 `dynamic = ["version"]` 或固定写入一个版本文件，其余位置全部动态读取。

---

## 7. 按严重程度汇总

| 严重程度 | 数量 | 代表性问题 |
|----------|------|------------|
| 🔴 **Critical** | 11 | `your-org` 占位符（4 处）、tracked `__pycache__`、`.gitignore` 路径错误、`sys.argv` 篡改、`notify.sh` URL 编码/JSON 转义缺失、`curl` 无 `--fail`、`ast-search.sh` 参数越界 |
| 🟡 **Warning** | 24 | 硬编码版本号、超时缺失、裸 except、原子写竞争、`list_states()` 不一致、测试缺失、分支不一致、pytest 未配置、文档缺失/不同步 |
| 🔵 **Info** | 12 | 文档字符串拼写、stdout/stderr 混淆、fsync 父目录、代码风格、冗余重定向 |

---

## 8. Out of Scope（本次审计未覆盖）

以下事项根据访谈阶段达成的规格，**未纳入本次审计**：

1. **实际代码修改** — 本报告为纯审计，未执行任何修复。
2. **Git 历史重写** — 仅建议 `git rm --cached`，未建议 `git filter-repo` 等历史重写操作。
3. **`kimi-cli-docs/` 与上游同步** — 43 个本地修改文件被视为有意增强，未与上游做 diff 对比。
4. **`omk/` 测试编写** — 仅识别缺口并给出策略建议，未实际编写测试代码。
5. **Skill 内容/指令重写** — 仅做结构与格式合规检查，未评估 Skill 的业务逻辑质量。
6. **Plugin 系统迁移** — `plugin.json` 迁移作为未来架构决策，未强制要求。
7. **二进制文件迁出** — Git LFS/CDN 仅作建议，未执行 `.gitattributes` 修改。
8. **Node.js/npm OMK CLI** — 仅审计本地 Python/Shell 代码库。
9. **`.specstory/` 内容** — 视为 IDE 会话产物，非项目源码。

---

*本报告由 Deep Interview + 并行审计 Agent 生成，所有发现均基于当前代码库快照与 `kimi-cli-docs/zh/` 官方规则基线。*
