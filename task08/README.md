# Task 08｜Agent 记忆系统 + PowerContext 设计与实现实践

> Datawhale《Easy Data × AI：构建知识与记忆驱动的 Agent》  
> 学习内容：D4《记哪些、忘哪些？—— Agent 记忆系统开发》+ I7《PowerContext 的设计与实现》

## 1｜这次 Task08 主要做了什么

Task08 是目前为止我实际操作量最大的一次任务。

D4 主要围绕 Agent 的记忆系统展开。除了运行课程中的 `d4_1` 到 `d4_8`，我还额外把当前版本的 PowerMem 跑通，并做了一个自己的 Memory Agent 实验。

I7 则继续使用 Task07 已经搭好的 PowerContext 环境，实际验证了：

- PreparedContext 的预算控制；
- Memory citation 和版本；
- Handoff 的准备、读取、提交和跨会话恢复；
- Memory retire 后的历史引用；
- 冲突 Memory 的人工裁决；
- Scope 隔离；
- Handoff acknowledgement。

这次最大的感受是：

> Agent 有记忆，不只是“把聊天记录存下来”，真正困难的是：记什么、怎么取、什么时候忘、如何避免污染、冲突时谁做决定，以及历史应该怎样保留。

---

## 2｜D4：先从 ReAct Agent 开始

`d4_1` 先让我重新理解了一个最基本的 Agent 循环：

```text
Reasoning
→ Acting
→ Observation
→ Reasoning
→ ...
→ Final Answer
```

实际运行中比较直观的一点是：一次模型推理并不一定只产生一个工具调用。例如同时询问北京、东京天气和人民币兑日元信息时，模型可以在同一步生成多个 `tool_calls`，然后统一读取工具结果再继续推理。

另外课程代码设置了 `max_steps`。这一点看起来很简单，但实际上很重要：

```text
Agent 能持续行动
≠
Agent 应该无限行动
```

Agent loop 必须有明确的停止条件和安全边界。

---

## 3｜没有 Memory 时，“像记得”不等于真的记得

运行 `d4_2` 时，连续进行了多轮技术问答。前几轮因为对话消息仍然保留在当前上下文里，Agent 看起来能够延续话题。

但是重新开始后再说：

```text
继续昨天的话题
```

Agent 只能给出泛化回答，并不能真正恢复之前的具体状态。

这让我更明确地区分了：

```text
语言上的连续感
≠
状态连续性
≠
持久 Memory
```

LLM 很容易生成“听起来像还记得”的回答，但如果没有明确的状态存储和恢复机制，本质上仍然只是当前 Prompt 内的上下文推断。

---

## 4｜D4_3：语义 Memory 开始真正影响回答

`d4_3` 中保存了几条用户信息，例如：

```text
我是 Python 开发者
主要做后端
喜欢简洁回答
```

后续再询问 Web 框架、缓存和数据库时，Agent 已经会根据这些信息调整推荐内容。

例如：

```text
Python + 后端
→ 推荐 FastAPI

Python 技术栈
→ 缓存方案更偏 Redis 等常见 Python 组合
```

这一步让我第一次比较直观地看到：

> Memory 的价值并不是“回答用户我记得你是谁”，而是它能够改变后续任务的选择和回答方式。

不过这个示例里的 Memory 主要还是单次程序运行中的实验状态，并没有解决跨进程持久化问题。

---

## 5｜D4_4：跨进程持久 Memory

`d4_4` 进一步加入持久化。

第一次运行结束后保存了多条 Memory，退出程序并重新启动，之前的信息仍然能够被读取。

例如再次询问：

```text
我之前说过我在哪种公司工作来着？
```

Agent 能恢复：

```text
SaaS 创业公司
```

这说明 Memory 已经不再依赖当前 Python 进程。

不过运行过程中也发现一个很实际的问题：Memory 数量会持续增加，而且会产生重复和推测性内容。

例如出现了类似：

```text
用户可能使用 Python 技术栈（因助手推荐 Python 相关方案）
```

这种 Memory。

这并不是用户明确说过的事实，而是从助手自己的回答反推出来的。这个问题后来在 PowerMem 实验中表现得更加明显。

---

## 6｜D4_5：多用户隔离不能靠“搜索后过滤”

`d4_5` 中创建了 Alice 和 Bob 两个用户。

正常情况下：

```text
Alice → 3 条 Memory
Bob   → 2 条 Memory
```

Bob 搜索 Alice 的花生过敏信息时没有结果。

但课程故意提供了一个不带正确隔离条件的查询：

```text
search_without_isolation
```

结果 Bob 可以看到 Alice 的：

```text
花生过敏
```

这说明多用户系统里一个非常重要的原则：

> 隔离条件应该进入查询本身，而不是先把所有数据查出来，再在应用层过滤。

另外还验证了：

- Bob 无法删除 Alice 的 Memory；
- Alice 可以删除自己的 Memory；
- Alice 可以显式把某条 Memory 共享给 Bob；
- Bob 能读取共享内容，但不能修改 Alice 的原始 Memory。

因此：

```text
user_id
→ 不只是检索标签
→ 也是数据安全边界
```

---

## 7｜D4_6：Memory 不能无限堆积

`d4_6` 重点测试压缩、整合和 Profile。

10 轮原始对话：

```text
约 289 tokens
```

抽取成 Memory facts 后：

```text
约 73 tokens
```

压缩比大约：

```text
4 : 1
```

在 Top5 上下文中：

```text
原始文本约 154 tokens
facts 约 34 tokens
```

还测试了 Flask → FastAPI 的迁移整合：

```text
零散事实
→ 合并
→ 用户后端已从 Flask 迁移到 FastAPI
```

原有 3 个相关碎片被归档。

这一部分让我理解了一个比较重要的区别：

```text
存得更多
≠
记得更好
```

长期 Memory 如果只追加、不整理，最终会导致重复、冲突、检索噪音和 Prompt 膨胀。所以记忆系统本身也需要“维护”。

---

## 8｜D4_7：Hot / Warm / Cold 分层

`d4_7` 将 Memory 分成：

```text
Hot
Warm
Cold
```

初始状态：

```text
Hot  = 2
Warm = 1
Cold = 2
```

普通日常搜索不会自动带回 Cold Memory。

但显式允许 `include_cold` 后，可以重新找到旧的 ECS / Docker / FastAPI 信息。

实验中还把 RabbitMQ 从 Warm 降到 Cold，又把一条 Cold Memory 重新升回 Hot。

这里让我理解了：

> “忘记”不一定等于删除。

很多时候更合理的是：

```text
降低优先级
→ 退出高频检索面
→ 必要时仍可恢复
```

所以：

```text
降权负责排序
分层负责是否进入热检索面
删除才是真正移除
```

---

## 9｜D4_8：清理 Memory 之前先 dry-run

`d4_8` 实际模拟了多种 Memory：

- 长期重要信息；
- 正在使用的信息；
- 临时偏好；
- 已经过期的信息；
- 其他用户的信息。

清理流程首先运行：

```text
dry-run
```

得到：

```text
archived = 2
deleted = 1
kept = 1
protected_skipped = 1
```

dry-run 阶段并不会实际修改数据。

正式执行后：

- 受保护信息只归档，不硬删除；
- 活跃信息继续保留；
- 已废弃框架信息执行 hard delete；
- 主存储、向量索引和 cache 同时清理；
- 没有留下 ghost record；
- Alice 的清理不会影响 Bob。

这一部分可以总结成：

```text
KEEP
→ ARCHIVE
→ DELETE
```

以及：

> 先压缩，再分层，最后才考虑硬删除。

---

## 10｜PowerMem：课程 API 和当前版本已经不同

课程示例里的 PowerMem API 类似：

```python
from powermem import PowerMem

memory = PowerMem(user_id="...")
```

但我实际安装的是：

```text
powermem 1.1.7
```

当前 API 已经变成：

```python
from powermem import Memory, auto_config

memory = Memory(config=auto_config())
```

写入和搜索也变成：

```python
memory.add(..., user_id="...")
memory.search(..., user_id="...")
```

通过 introspection 实际确认：

```text
PowerMem = False
Memory = True
auto_config = True
```

所以这次没有机械照抄教程，而是根据当前安装版本重新适配。

---

## 11｜PowerMem 环境踩坑：Windows embedded seekDB 不可用

一开始 PowerMem 默认 OceanBase / seekDB 配置会尝试使用 embedded 模式。

在 Windows 环境下初始化时失败，核心原因是：

```text
pylibseekdb 只支持 Linux
```

最终改成已经启动的 seekDB Server：

```text
host: 127.0.0.1
port: 2881
database: easy_data_x_ai_demo
```

并给 PowerMem 单独设置 OceanBase Server 参数。

之后 Memory 初始化成功，实际配置包括：

```text
LLM provider: OpenAI-compatible
LLM model: deepseek-ai/DeepSeek-V3
API provider: SiliconFlow
Embedding: all-MiniLM-L6-v2
Embedding dimensions: 384
Vector store: OceanBase / seekDB Server
```

这里也让我发现：

> 同一个底层数据库产品，“embedded”和“server”是完全不同的运行方式，不能只看到 seekDB 名称相同就认为环境一定兼容。

---

## 12｜模型配置踩坑：placeholder 不是 API Key

PowerMem 最初自动读取到 Qwen 配置，但 `.env` 中的 DashScope Key 实际还是教程 placeholder，因此请求返回认证失败。

后来切换到 SiliconFlow 的 OpenAI-compatible API 后，Memory extraction 才真正跑通。

实际第一次成功抽取到：

```text
我是一个 Python 开发者
在一家做 SaaS 产品的创业公司工作
喜欢简洁的回答
```

随后执行搜索，也能够正常找回这三条内容。

这一步算是第一次完整跑通：

```text
用户消息
→ LLM Memory extraction
→ seekDB / OceanBase 持久存储
→ Memory search
→ 返回长期记忆
```

---

## 13｜自己写了一个 PowerMem Memory Agent

除了课程示例，我额外写了：

```text
task08/d4_powermem_experience.py
```

流程是：

```text
用户输入
→ search_memory
→ 将相关 Memory 注入 system prompt
→ 调用 LLM
→ 得到回答
→ memory.add
→ 下一轮继续
```

实际进行了 5 轮对话：

1. Python 开发者 + SaaS 创业公司；
2. 喜欢简洁回答；
3. 推荐消息队列；
4. 团队用过 RabbitMQ，觉得配置复杂；
5. 询问 Celery。

退出脚本重新启动后，再问：

```text
我之前说过我在哪种公司工作来着？
```

能够回答：

```text
做 SaaS 产品的创业公司
```

因此跨进程持久化也实际验证成功。

---

## 14｜我遇到的 Memory 污染问题

自己的 Agent 第一次实现时，把：

```text
user message
+
assistant answer
```

一起交给 PowerMem extraction。

结果出现了一个很典型的问题。

用户只说：

```text
RabbitMQ 配置太复杂
```

助手回答：

```text
可以试试 Celery + Redis
```

后续 PowerMem 却把：

```text
推荐试试 Celery + Redis，更轻量适合 SaaS 场景
```

也保存成了 Memory。

下一轮搜索时，这条助手自己生成的建议又被召回，再影响下一轮回答。

继续询问数据库方案时，Agent 甚至出现了类似：

```text
你们已经在用了
```

这样的错误暗示。

形成的链条是：

```text
助手建议
→ 被错误写成用户事实
→ 下一轮召回
→ 助手把自己过去的建议当成真实背景
→ 再生成新的推断
→ 再写入 Memory
```

这是这次 D4 对我最有价值的发现之一。

我现在更倾向于认为：

> Memory extraction 必须区分事实来源，至少要区分 user-declared、assistant-generated、tool-observed 和 inferred，不能把所有对话文本无差别沉淀成长期事实。

---

## 15｜I7：PreparedContext 不只是 Memory Search

I7 继续使用 Task07 已经搭好的 PowerContext 1.0.0。

原 Scope：

```text
scope_id: scp_2c75f20zm2ygqx2mx77y0fyrha
title: I6 Aurora lab
```

先创建短测试 Memory：

```text
Context lab entry remains available across sessions.
```

随后又添加一条专门用于预算实验的长 Memory。

在：

```text
max_bytes = 8000
```

时，两条 Memory 都能完整进入 PreparedContext：

```text
status = ready
content_bytes = 1693
```

但：

```text
max_bytes = 512
```

时返回：

```text
status = empty
content = null
content_bytes = 0
```

而且重复执行结果一致。

这说明预算计算的并不只是 Memory 正文字数，还包括 Safety header、Scope、Artifact revision、citation、entry metadata、Markdown 格式等渲染开销。

---

## 16｜预算不足时，不会因为第一条太长就停止

为了进一步验证 PreparedContext 的装配逻辑，我让：

```text
长 Memory → Recall rank 1
短 Memory → Recall rank 2
```

两条一起完整输出时：

```text
content_bytes = 1731
```

短 Memory 单独完整输出需要：

```text
685 bytes
```

然后把预算精确设置成：

```text
max_bytes = 685
```

最终结果是：

```text
长 Memory：没有进入输出

短 Memory：
Recall rank: 2
Truncated: no

content_bytes = 685
```

也就是说：

> 排名第 1 的长候选放不下时，PowerContext 不会立即停止，而是继续尝试后面的候选。

特别是 `Recall rank: 2` 仍然被保留下来，说明短 Memory 并没有被重新排成第一名。

---

## 17｜Prepared Handoff 和持久 Handoff 是两件事

接下来使用 `handoff_current_work` 准备当前实验状态。

第一次调用返回 HTTP 422。

后来检查发现 `handoff_current_work` 的 schema 很严格：

```text
scope_id
source_id
handoff
```

并且 WorkClaim 中：

```text
basis = verified
→ 必须提供 exact evidence

basis = declared
→ evidence 必须为空
```

Memory citation 也不能直接裸传，而需要包装成：

```json
{
  "kind": "memory",
  "memory_citation": {
    "...": "..."
  }
}
```

修正结构后成功获得：

```text
schema: powercontext.prepared-handoff.v1
base: null
```

随后使用：

```text
selection = prepared
```

调用 `continue_handoff`，结果：

```text
status = resolved
selected_revision = null
current_revision = null
```

说明 Prepared Handoff 可以被读取，但此时还没有持久 Revision。

---

## 18｜commit 后跨会话恢复 Handoff

确认 Prepared Handoff 内容以后，再显式调用：

```text
commit_handoff
```

得到：

```text
family: handoff
artifact_id: handoff
revision: 1
```

然后退出 Codex，新开一个完全新的会话。

使用：

```text
selection = exact
revision = handoff revision 1
```

成功恢复 objective、5 条 state、next_action、omissions 和 evidence_checks。

并且：

```text
selected_revision = revision 1
current_revision = revision 1
```

这一部分让我理解了 Handoff 的意义：

> Handoff 不是聊天摘要，而是一个带证据、可提交、可精确引用的工作交接快照。

---

## 19｜Handoff 的历史内容不会自动更新

Handoff Revision 1 里保存的 `next_action` 和 `omissions`，在后续实验已经完成后，重新读取 Revision 1 时仍然保持原来的文字。

例如仍然会显示：

```text
尚未提交持久 Handoff revision
```

但实际上此时 revision 1 已经存在。

这不是数据错误，而是因为：

```text
Handoff Revision 1
=
提交当时的不可变快照
```

它不是一个自动维护的“当前任务看板”。

---

## 20｜retire Memory 不等于删除历史

完成实验后，分别停用了短测试 Memory 和长预算 Memory。

短 Memory：

```text
revision 4 → revision 5
state: active → inactive
```

长 Memory：

```text
revision 5 → revision 6
state: active → inactive
```

停用以后，`search_memory` 已经不会再返回这些条目。

但使用停用前保存的旧 citation（Memory revision 4），仍然能够精确读取当时的正文和：

```text
state = active
```

因此：

```text
当前 revision：
inactive

旧 revision：
active
```

两者并不冲突。

这让我更清楚地区分了：

```text
当前准入状态
≠
历史快照
```

---

## 21｜Memory retire 后，旧 Handoff evidence 仍然可用

两条测试 Memory 都已经 inactive 后，再次读取：

```text
Handoff Revision 1
```

结果：

```text
Handoff 内容仍然存在
旧 Memory citation 仍然存在
evidence_checks 仍然全部 available
```

也就是说，retire Memory 并不会破坏已经持久化到 Handoff 中的历史精确引用。

所以这里实际上有三层不同概念：

```text
当前 search 是否召回
≠
旧 citation 是否可以读取
≠
Handoff 中的历史 evidence 是否仍可解析
```

---

## 22｜Scope 隔离实验踩坑

I7 的可选冲突实验要求新建独立 Scope。

新 Scope：

```text
scope_id: scp_4bwey3c20v4pa8r3axt80ypa5a
title: I7 Conflict Memory Lab
```

一开始虽然调用了 `set_scope_binding`，但 Proposal A 仍然误写进了旧 Scope。

后来发现原因是当前 shell 已经设置：

```bash
POWERCONTEXT_CODEX_SCOPE_ID
```

Codex 启动时 Scope 解析优先级是：

```text
显式 POWERCONTEXT_CODEX_SCOPE_ID
→ Session binding
→ workspace binding
→ Server default Scope
```

而且 Agent 自己在 Memory 写入工具中传一个别的 `scope_id`，并不能把写操作随意重定向到另一个 Scope。

最终先把误写的 Proposal A retire，再退出 Codex，在 shell 中改为：

```bash
export POWERCONTEXT_CODEX_SCOPE_ID='scp_4bwey3c20v4pa8r3axt80ypa5a'
```

重新启动 Codex 后才正确进入新 Scope。

这个失败反而让我更直观地理解了：

> Scope 不只是普通业务参数，也是写操作的安全边界。

---

## 23｜冲突 Memory 不应该由 Agent 自动裁决

在独立 Scope 中保存了两个尚未定稿的约束：

Proposal A：

```text
request timeout = exactly 30 seconds
NOT FINAL
```

Proposal B：

```text
request timeout = exactly 120 seconds
NOT FINAL
```

搜索时两条都能召回。

这时没有让 Agent 根据哪条更新、哪条更合理、哪条更符合经验自动选择，而是明确把两个 citation 都展示出来，再由我自己选择：

```text
A：30 秒
```

然后：

```text
revise A
→ 去掉 NOT FINAL
→ 成为 FINAL 30 秒约束

retire B
→ 120 秒 Proposal 退出当前召回
```

最终正常搜索只剩：

```text
FINAL：30 seconds
```

这说明：

> Memory 系统负责保存、检索和版本管理，但冲突裁决本身不应该天然属于 retrieval 层。

---

## 24｜revision、entry_id 和 entry_version_id

冲突实验也让我真正理解了 PowerContext 的三个版本概念。

A 修订前：

```text
entry_id:
mem_ent_e87a9dfeb9b74e239b29852f9031abb3

entry_version_id:
mem_ver_407be4e80f1344a89d121c5fe3e9f026
```

A 修订以后：

```text
entry_id:
仍然相同

entry_version_id:
变为 mem_ver_227ad84864b64428aee78e11007a071e
```

所以：

```text
Memory Artifact revision
→ 整个 Memory 集合某个时刻的快照

entry_id
→ 一条逻辑 Memory 的稳定身份

entry_version_id
→ 这条 Memory 某次具体正文版本
```

而 B 被 retire 时：

```text
entry_version_id 没有变化
state: active → inactive
```

说明：

> 正文版本变化和生命周期状态变化也是两个不同维度。

---

## 25｜Handoff acknowledgement

最后还补做了：

```text
acknowledge_handoff
```

先读取 exact Handoff Revision 1，再提交：

```text
status: accepted
selection: exact
```

同时明确：

```text
live_state: confirmed
capability: confirmed
authorization: confirmed
```

PowerContext 成功创建：

```text
kind: handoff-receipt
source_id: i7-handoff-receipt-20261006-01
```

这让我理解了：

```text
continue_handoff
→ 表示“我读到了交接”

acknowledge_handoff
→ 表示“我作为接收方对这次交接做出回执”
```

两者不是一回事。

---

## 26｜我现在对 Agent Memory 的理解

做完 Task08 后，我觉得一个比较完整的 Agent Memory 系统至少要处理下面几个问题。

### 26.1 记什么

不能什么都记。

比较适合长期保存的是：

- 稳定事实；
- 用户明确偏好；
- 已确认决策；
- 长期约束；
- 可复用任务结果。

而助手自己的临时建议、未经确认的推断和聊天里的偶然信息，不应该轻易进入长期 Memory。

### 26.2 怎么想起来

召回不是越多越好。

需要考虑：

```text
相关度
版本
状态
Scope
来源
优先级
预算
```

PreparedContext 的实验说明，即使 Memory 已经召回，也还需要经过一次上下文装配。

### 26.3 怎么忘

忘记并不只有 delete。

可以是：

```text
降权
→ Hot / Warm / Cold 分层
→ Archive
→ Retire
→ Hard Delete
```

不同信息需要不同生命周期。

### 26.4 怎么避免“记错”

我这次实际遇到最严重的问题，就是助手自己的输出被重新保存为用户事实。

因此以后设计 Memory Agent 时，我会优先增加：

```text
source attribution
```

至少区分：

```text
user-declared
assistant-generated
tool-observed
inferred
human-confirmed
```

### 26.5 谁拥有最终决定权

冲突实验给出的答案比较明确：

```text
Memory 可以保存多个候选事实
Agent 可以发现冲突
Agent 可以展示证据
但最终业务决策不应被 retrieval 自动替代
```

特别是涉及关键约束时，应该显式进入人工确认或独立 Review 流程。

---

## 27｜Task08 的主要踩坑与修正

这次遇到的真实问题比之前多很多：

| 问题 | 原因 | 最终处理 |
|---|---|---|
| PowerMem 教程 API 无法直接使用 | 当前 1.1.7 API 已变化 | 改用 `Memory + auto_config` |
| Windows embedded seekDB 初始化失败 | `pylibseekdb` 依赖 Linux | 改用 seekDB Server |
| Qwen 调用返回 401 | `.env` 仍是 placeholder | 改为实际可用的 OpenAI-compatible provider |
| Memory 中出现助手自己的建议 | user + assistant 一起参与 extraction | 识别出 source attribution 问题 |
| Handoff 返回 422 | WorkClaim / evidence schema 不符合要求 | 按 exact schema 重建 payload |
| 新 Scope 写入仍落到旧 Scope | `POWERCONTEXT_CODEX_SCOPE_ID` 优先级更高 | 修改环境变量并新开 Codex session |
| 当前 search 与旧 citation 状态不同 | 当前状态和历史快照语义不同 | 分开理解 admission 与 historical reference |

这些失败其实比“所有命令第一次就成功”更有价值，因为它们暴露了真实 Agent 系统最容易出问题的位置。

---

## 28｜这次最终跑通的完整链路

D4：

```text
ReAct
→ 对话上下文
→ 语义 Memory
→ 持久 Memory
→ 多用户隔离
→ 压缩与整合
→ Hot / Warm / Cold
→ dry-run + 生命周期清理
```

PowerMem：

```text
用户输入
→ Memory search
→ Prompt 注入
→ LLM 回答
→ Memory extraction
→ seekDB 持久化
→ 跨进程召回
→ 发现 Memory 污染问题
```

PowerContext：

```text
Memory
→ exact citation
→ PreparedContext
→ byte budget
→ Prepared Handoff
→ continue(prepared)
→ commit
→ exact Revision
→ 跨 Session 恢复
→ acknowledge
→ Memory retire
→ 历史 citation
→ 冲突发现
→ 人类裁决
→ revise + retire
```

---

## 29｜这次 Task08 对我最重要的几个认识

如果只保留几个结论，我会记住：

1. **Memory 不是聊天记录。**  
   它应该保存未来仍然值得复用的信息。

2. **能写入 Memory 不代表应该写入 Memory。**  
   错误 Memory 比没有 Memory 更危险。

3. **Source attribution 很重要。**  
   用户事实、助手建议、工具观察和模型推断不能混为一谈。

4. **当前有效与历史存在是两回事。**  
   retire 可以让内容退出召回，但不应该破坏可审计历史。

5. **上下文预算本身就是系统设计的一部分。**  
   Retrieval 之后仍然需要 Context Assembly。

6. **Scope 是安全边界，不只是分类标签。**

7. **冲突事实不能自动按“最新”解决。**  
   没有明确决策权时，Agent 应展示冲突，而不是替用户决定。

8. **Handoff 是可引用的工作快照，不是自动更新的任务看板。**

---

## 30｜本次实践文件

自己增加的 PowerMem 实验代码：

```text
task08/d4_powermem_experience.py
```

主要用于验证：

```text
PowerMem 1.1.7
+ SiliconFlow OpenAI-compatible LLM
+ seekDB Server
+ Memory search / injection / extraction
+ 跨进程持久化
+ Memory 污染问题
```

> 安全说明：仓库中不提交 `.env`、API Key、Token 或其它凭据。

---

## 31｜参考资料

- Datawhale Easy Data × AI：<https://github.com/datawhalechina/easy-data-x-ai>
- D4《Agent 开发与记忆系统》：<https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/dev/D4%20%E8%AF%BE%E7%A8%8B%E7%A8%BF%EF%BC%9AAgent%20%E5%BC%80%E5%8F%91%E4%B8%8E%E8%AE%B0%E5%BF%86%E7%B3%BB%E7%BB%9F.md>
- I7《PowerContext 的设计与实现》：<https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/industry/I7%20%E8%AF%BE%E7%A8%8B%E7%A8%BF%EF%BC%9APowerContext%20%E7%9A%84%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%AE%9E%E7%8E%B0.md>
- PowerContext：<https://github.com/oceanbase/powercontext>
