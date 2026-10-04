# Task 07｜Skill 与 Agent 知识管理 + 上下文工程实践

> Datawhale《Easy Data × AI：构建知识与记忆驱动的 Agent》  
> 学习内容：P4《Skill 与 Agent 知识管理》+ I6《上下文工程概述》

## 1｜P4：Skill 与 Agent 知识管理

这部分我重点理解了 Skill 和程序记忆之间的关系。

程序记忆更像 Agent 内部“遇到这种情况应该怎么做”的行为规则，而 Skill 是把这类经验外化成可以管理、共享、检索和复用的文档。相比普通 Prompt，Skill 更适合沉淀稳定、可重复使用的任务流程。

按照课程里的思路，一个比较完整的 Skill 至少应该把名称、适用场景、输入范围和示例写清楚，否则内容虽然人能看懂，但 Agent 不一定能稳定判断什么时候应该使用。

### 1.1 我目前使用的 Skill / Rules / Instructions 盘点

结合自己现在实际在用的 Personal AI OS，简单盘点如下：

| 平台 / 工具 | 当前主要承载内容 | 主要载体 | 当前问题 |
|---|---|---|---|
| ChatGPT | Project 指令、角色规则、任务方法 | Project Instructions、自定义指令 | 与其他平台难直接复用 |
| Coze | 角色提示词、工作流、知识配置 | Bot / Workflow | 平台绑定较强 |
| WorkBuddy | 执行角色、长期记忆、套件规则 | 角色描述、记忆、套件 | 外部迁移不方便 |
| Codex | 项目规则、代码任务方法 | AGENTS.md、Skills、Plugins | 结构化程度较高 |
| Octop | Workspace 规则、Agent 配置 | AGENTS.md、Workspace 配置 | 还需要跨平台适配 |
| DeepSeek Harness | Workspace / Agent 行为规则 | Workspace 配置、Prompt | 与其他宿主格式不同 |

### 1.2 我目前的碎片化问题

课程里提到 Skill 的碎片化主要发生在项目、工具和人员三个层面。放到我自己的使用场景里，比较明显的是：

- 项目隔离：同一套方法会分别出现在不同 Project、Workspace 或仓库中；
- 工具隔离：ChatGPT、Codex、Coze、WorkBuddy、Octop、Harness 的规则格式和加载方式不同；
- 多 Agent 隔离：不同角色之间不会天然共享彼此的程序性知识。

目前最快的复用方式还是把 Markdown、AGENTS.md、SKILL.md 等内容手工复制到不同平台，再按各平台格式做适配。但这种方式的问题也很直接：重复维护、版本容易分叉、更新不能自动同步，也很难判断哪个版本才是当前权威版本。

这部分学习后，我更倾向于把稳定、跨任务、可复用的方法沉淀成独立 Skill，再由不同宿主去加载，而不是让同一套规则长期散落在多个 AI 平台里各自演化。

## 2｜I6：上下文工程概述

I6 这部分让我更清楚地区分了提示词工程和上下文工程。

提示词工程主要解决“这次任务应该怎么说清楚”；上下文工程还要解决“哪些信息应该进入这次请求、这些信息从哪里来、是否仍然有效、如何控制大小、如何跨会话继续，以及后续如何修订和交接”。

课程里把上下文拆成了几类不同职责：Source、Memory、Task State、Prepared Context 和 Handoff。它们不是同一件事，尤其是长期保存的信息和一次请求临时需要看到的内容，需要分开处理。

## 3｜PowerContext 实操环境

本次按照 I6 的官方教程，在 WSL2 的 Ubuntu 环境中完成 PowerContext 实验。

实际环境：

```text
Ubuntu 24.04.5 LTS
Python 3.12.3
Git 2.43.0
curl 8.5.0
uv 0.12.23
Codex CLI 0.160.0
PowerContext 1.0.0
```

PowerContext 检查结果：

```text
server liveness: ok
server readiness: ok
runtime: ready
database: ready
```

当前能力中 memory、skill、handoff 等 Artifact family 均已启用；本次未配置自动 Memory extraction，所以主要通过显式 Memory 写入、搜索和修订完成练习。

## 4｜MCP、Skill、Plugin 接入

PowerContext 接入 Codex 后，实际确认：

- PowerContext MCP：connected，共 33 tools；
- `project-context` Skill 可以被 Codex 找到并读取；
- 3 个 Hook 已安装并完成信任：`PreToolUse`、`SessionStart`、`UserPromptSubmit`；
- 实际调用到了 `resolve_scope_binding`、`remember_memory`、`search_memory`、`get_memory_entry`、`revise_memory_entry` 等工具。

这次也更直观地理解了三者的分工：

```text
Skill：告诉 Agent 这类任务应该怎么做
MCP：让 Agent 能发现和调用外部上下文工具
Agent Plugin：把 Skill、MCP 配置以及 Hook 集成到宿主里
```

## 5｜Scope 绑定踩坑

一开始虽然 PowerContext 已经连接成功，但 Codex 实际解析到的是 Default Scope，而不是我为课程练习新建的 `I6 Aurora lab`。

后来重新显式设置：

```bash
export POWERCONTEXT_CODEX_SCOPE_ID='scp_2c75f20zm2ygqx2mx77y0fyrha'
export POWERCONTEXT_CODEX_CAPTURE_PROMPTS=false
```

并使用新的 Codex 会话重新检查，最终确认：

```text
scope_id: scp_2c75f20zm2ygqx2mx77y0fyrha
title: I6 Aurora lab
```

这一步让我意识到，PowerContext Server 连接成功并不代表当前 Agent 一定绑定到了正确的工作范围。做跨会话实验前，Scope 本身也需要显式核对。

## 6｜会话 A：保存 7 天退款范围

在正确 Scope 下，通过 `project-context` Skill 保存：

```text
Aurora refund report covers the last 7 days.
```

类型：

```text
kind: decision
```

保存后立即使用 `search_memory` 搜索 `Aurora refund report`，成功命中。

第一次版本：

```text
revision: 1
entry_id: mem_ent_5c98cb4b5697413598bdd24f263d1189
entry_version_id: mem_ver_bddea76febe64ea091a5d01d1e5c8631
```

## 7｜会话 B：跨会话找回 7 天决定

退出原 Codex 会话后重新启动新会话，不把“7 天”答案告诉新会话，只要求 PowerContext 搜索当前 Scope 中的 `Aurora refund report`。

实际结果：

```text
找到 1 条记忆
Aurora refund report 的退款统计范围为最近 7 天
mode 请求为 auto，实际检索模式为 fts
```

返回的 `entry_id` 和 `entry_version_id` 与会话 A 一致。

这一步验证了：Memory 不依赖原来的 Codex 对话，而是跟随 Scope 在不同 Session 之间持续存在。

## 8｜7 天修改为 14 天

继续在会话 B 中读取当前条目，然后使用当前 citation 调用 `revise_memory_entry`，把正文改为：

```text
Aurora refund report covers the last 14 days.
```

修订完成后再次搜索，当前结果已经变为最近 14 天。

新的版本信息：

```text
revision: 2
entry_id: mem_ent_5c98cb4b5697413598bdd24f263d1189
entry_version_id: mem_ver_956e56ac9a3f4d828afffb1f0aca50ac
```

可以看到 `entry_id` 没变，但 `entry_version_id` 已变化，说明是同一条 Memory 的新版本。

## 9｜旧 citation 读取历史版本

修订以后，继续使用 revision 1 的旧 citation 调用 `get_memory_entry`。

实际仍然能读取：

```text
Aurora refund report covers the last 7 days.
```

因此本次完整跑通了：

```text
保存 Memory
→ 新会话跨会话读取
→ 修订当前版本
→ 搜索确认新版本
→ 用旧 citation 回读历史版本
```

这部分让我更直观地理解了 citation 的作用。它不只是简单的“来源链接”，还可以精确定位到具体 Memory、entry 和历史版本。

## 10｜这次对上下文工程的理解

以前我更容易把“上下文”理解成聊天记录或者把更多历史内容塞进上下文窗口。做完这次实验以后，我觉得上下文工程更接近“为当前任务准备一份可控、可追溯、可维护的工作视图”。

几个比较直接的认识：

- Scope 和 Session 不是一回事，Session 结束以后 Scope 里的工作上下文仍然可以继续使用；
- Memory 不是完整聊天记录，而是后续仍值得继续使用的结论；
- 当前版本和历史版本需要同时可追溯，不能简单覆盖；
- 检索命中不代表信息一定可信，还需要看版本、来源和适用范围；
- `Prepared ≠ Injected ≠ Used ≠ Benefited`，本次能够确认检索、读取和实际使用，但没有做严格 A/B 测评，所以不额外声称任务效率已经得到量化提升。

## 11｜参考资料

- Datawhale Easy Data × AI：<https://github.com/datawhalechina/easy-data-x-ai>
- P4《Skill 与 Agent 知识管理》：<https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/pm/P4%20课程稿：Skill%20与%20Agent%20知识管理.md>
- I6《上下文工程概述》：<https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/industry/I6%20课程稿：上下文工程概述.md>
- PowerContext：<https://github.com/oceanbase/powercontext>
- PowerContext Codex Integration：<https://github.com/oceanbase/powercontext/blob/powercontext-v1.0.0/docs/zh/docs/integrations/codex.md>
