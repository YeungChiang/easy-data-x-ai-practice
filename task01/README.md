# Task 01｜环境准备与课前导读

> Datawhale《Easy Data × AI：构建知识与记忆驱动的 Agent》学习记录  
> 状态：✅ 已完成

## 1｜本次学习内容

Task 01 主要完成两部分内容：

- Shell、Python、模型 API、Git / GitHub 环境准备与自检
- F0、F1、F2 公共基础学习

---

## 2｜环境自检结果

| 项目 | 当前状态 | 结果 |
|---|---|---|
| Shell | Windows PowerShell | ✅ 通过 |
| Python | 3.12.10 | ✅ 通过 |
| pip | 25.0.1 | ✅ 通过 |
| Git | 2.49.0.windows.1 | ✅ 通过 |
| Git 默认分支 | `main` | ✅ 已配置 |
| Git 提交邮箱 | GitHub `noreply` 邮箱 | ✅ 已配置 |
| GitHub | 已完成官方仓库 Clone、个人仓库 Commit / Push | ✅ 通过 |
| Python 虚拟环境 | `.venv` | ✅ 已创建 |
| 课程依赖 | 已安装 | ✅ 通过 |
| SiliconFlow API | 已完成真实模型调用 | ✅ 通过 |

### 模型 API 自检

本次使用课程官方示例完成真实模型 API 测试：

- API 服务：SiliconFlow（硅基流动）
- 测试模型：`tencent/Hunyuan-MT-7B`
- 测试脚本：`D1/d1_1_base.py`
- 测试问题：`什么是 RAG？`
- 结果：成功获得模型返回，API 链路已跑通

完整链路可以概括为：

> Python → 虚拟环境 → 课程代码 → 本地 `.env` → SiliconFlow API → 模型 → 返回结果

安全方面，真实 API Key 只保存在本地 `.env` 文件中，不写入学习笔记，也不提交到 GitHub。

---

## 3｜F0：OpenClaw 为什么越用越好用？

我原来容易把“Agent 越用越聪明”理解成：底层模型本身会因为长期使用而不断变强。

学习后我的理解是：

> Agent 越用越好用，很多时候并不是底层模型被个人持续训练，而是系统逐渐积累了与用户有关的记忆、经验、SOP、Skill 和上下文，并能够在后续任务中重新调用这些内容。

因此，真正值得长期积累的不只是某一个 AI 产品中的聊天记录，而是能够持续维护、校正和迁移的数据、知识、经验与方法。

这也让我重新理解了“主动形成 SOP”的意义：把反复验证有效的做事步骤，从临时经验逐渐沉淀成可重复执行的方法，未来再进一步封装为 Workflow 或 Skill。

---

## 4｜F1：大模型的本质与边界

这一节给我的一个重要提醒是：

> AI 应用效果不好时，不应该第一反应就是换更强的模型。

很多问题可能来自：

- 数据缺失
- 数据错误或过时
- 上下文不足
- 输入信息质量差
- 模型无法获得完成任务所需的外部信息

“Garbage In, Garbage Out”让我更直观地理解了：如果输入的数据本身质量低，最终输出也很难可靠。

所以后续做 AI 应用时，我需要先检查“模型看到了什么数据、这些数据是否正确”，而不是只关注模型参数和排行榜。

---

## 5｜F2：AI Agent 全景图

目前我对几个核心概念的理解如下。

### Agent

普通聊天 AI 可以先简化理解为：

> 用户输入 → 模型生成 → 返回结果

Agent 则可以形成循环：

> 感知 → 推理 → 行动 → 观察 → 再推理

它不仅生成答案，还可以调用工具、读取环境反馈，并据此决定下一步。

### RAG

RAG 的核心不是简单“收集和整理数据”，而是：

> 从外部知识源中检索当前任务真正需要的信息，并将这些信息补充进模型上下文。

### Memory

> 保存过去值得复用的信息，并在未来合适的任务中重新召回和使用。

### Skill

> 把经过验证的做事方法、步骤、规则和经验封装为可以重复使用的能力。

### MCP

> 为 Agent 连接外部工具、数据和服务提供标准化接口。

### Context Engineering

> 决定当前任务应该给模型什么信息、给多少、以什么形式组织。

现阶段我可以先用下面这组关系帮助自己建立整体框架：

> LLM 提供基础智能  
> Agent 负责持续行动  
> RAG 负责按需查知识  
> Memory 负责记经验  
> Skill 负责复用方法  
> MCP 负责连接外部工具和数据  
> Context Engineering 负责组织当前任务所需上下文

---

## 6｜真实踩坑与解决记录

### 6.1 `python` 命令最初并不是真正的 Python

最开始运行：

```powershell
python --version
```

没有正常显示版本。

进一步检查后发现，Windows 当前命中的只是 Microsoft Store 的应用执行别名，而不是完整 Python 环境。

最终安装 Python 3.12.10（64-bit），并将 Python 加入 PATH，之后：

```powershell
python --version
py --version
python -m pip --version
```

均恢复正常。

### 6.2 PowerShell 阻止虚拟环境激活脚本

创建虚拟环境：

```powershell
python -m venv .venv
```

成功后执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

被 PowerShell Execution Policy 拦截。

为了不直接修改系统级安全策略，本次改为显式调用虚拟环境里的 Python：

```powershell
.\.venv\Scripts\python.exe
```

并继续完成依赖安装和课程脚本运行。

### 6.3 GitHub 邮箱隐私导致第一次 Push 被拒绝

第一次 Push 时，GitHub Desktop 提示 Commit 中包含被设置为私密的真实邮箱，因此拒绝上传。

最终将 Git 提交邮箱改为 GitHub 提供的 `noreply` 邮箱，并重写尚未上传的首次 Commit 作者信息：

```powershell
git commit --amend --reset-author --no-edit
```

之后成功完成 Push。

### 6.4 API 跑通，不代表模型回答一定正确

同一个官方测试脚本连续运行两次，针对“什么是 RAG？”这个问题：

- 第一次将 RAG 错误解释为 `Relevant Annotation Guidance`
- 第二次才正确回答为 `Retrieval Augmented Generation`

这次现象让我把 F1 中“大模型输出可能出现事实性错误和不稳定性”的概念变成了真实体验。

因此后续做 Agent / RAG 应用时，我不能把“程序成功运行”等同于“结果可信”，还需要关注：

- 数据质量
- 上下文质量
- 输出验证
- 评测机制
- 事实来源

---

## 7｜Task 01 阶段总结

Task 01 对我最大的价值，不只是“安装好了 Python 和 Git”，而是第一次完整跑通了一套 AI 开发学习环境：

> GitHub 课程代码 → 本地开发环境 → Python 虚拟环境 → API 配置 → 调用真实模型 → Git 版本管理 → GitHub 学习成果沉淀

同时，我也开始把之前零散使用 AI 工具的经验，与 Agent、RAG、Memory、Skill、MCP 和 Context Engineering 等概念建立起关系。

下一阶段进入 Task 02 后，希望继续从“会使用 AI 工具”向“理解 AI 应用为什么这样设计、如何落地”推进。

---

## 参考资料

- Datawhale Easy Data × AI 官方仓库：  
  https://github.com/datawhalechina/easy-data-x-ai

- 在线课程：  
  https://datawhalechina.github.io/easy-data-x-ai