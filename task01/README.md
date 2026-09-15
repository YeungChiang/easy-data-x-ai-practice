# Task 01｜环境准备与课前导读

## 1\. 本次学习内容

本次 Task 主要包括两部分：

* Shell、Python、模型 API、Git 环境准备与自检
* F0、F1、F2 公共基础学习

\---

## 2\. 环境自检

### Shell

* Windows PowerShell：已正常使用

### Python

* Python：3.12.10
* pip：25.0.1
* 状态：通过

### Git

* Git：2.49.0.windows.1
* Git 用户名：Joe
* 默认分支：main
* 已配置 GitHub noreply 邮箱
* 状态：通过

### GitHub

* 已统一使用原 GitHub 主账号
* 已 Clone Datawhale 官方课程仓库
* 已建立个人课程实践仓库：
`easy-data-x-ai-practice`
* 已完成第一次 Commit / Push

### 模型 API

* 状态：待完成

\---

## 3\. F0｜我的理解

我原来容易把“Agent 越用越聪明”理解成模型本身会因为长期使用而不断变强。

学习后我的理解是：

Agent 越用越好用，很多时候并不是底层模型本身被持续训练，而是系统逐渐积累了与用户有关的记忆、经验、SOP、Skill 和上下文，并能够在后续任务中重新调用这些内容。

因此，真正值得长期积累的不只是某一个 AI 产品中的聊天记录，而是可以持续维护和迁移的数据、知识、经验与方法。

\---

## 4\. F1｜我的理解

一个重要认识是：

AI 应用效果不好时，不应该第一反应就是换更强的模型。

很多问题来自：

* 数据缺失
* 数据错误
* 数据过时
* 上下文不足
* 输入信息质量差

“Garbage In, Garbage Out”强调的也是：

> 输入数据质量低，最终输出就很难可靠。

\---

## 5\. F2｜我的理解

目前我对几个概念的理解：

### Agent

普通聊天 AI 主要是：

用户输入 → 模型生成 → 返回结果

Agent 则可以：

感知 → 推理 → 行动 → 观察 → 再推理

它能够持续执行任务，并根据环境反馈决定下一步。

### RAG

从外部知识源中检索当前任务真正需要的信息，并补充到模型上下文中。

### Memory

保存过去值得复用的信息，并在未来合适的场景中重新召回。

### Skill

把已经验证有效的做事方法、步骤和经验封装成可以重复使用的能力。

### MCP

为 Agent 连接外部工具、数据和服务提供标准化接口。

\---

## 6\. 当前形成的整体认识

目前我可以先把它们理解成：

> LLM 提供基础智能  
> Agent 负责持续行动  
> RAG 负责查知识  
> Memory 负责记经验  
> Skill 负责复用方法  
> MCP 负责连接外部工具和数据  
> Context Engineering 负责决定当前任务应该把什么信息交给模型

\---

## 7\. 当前问题与下一步

### 尚未完成

* 模型 API 自检
* Task 1 最终打卡整理

### 下一步

1. 跑通模型 API
2. 完成 Task 1 全部环境检查
3. 整理 Task 1 正式公开学习记录
4. 提交 Datawhale Normal 模式打卡

\---

## 参考资料

* Datawhale Easy Data × AI：
https://github.com/datawhalechina/easy-data-x-ai
* 在线课程：
https://datawhalechina.github.io/easy-data-x-ai

