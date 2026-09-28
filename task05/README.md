# Task05｜Agent 记忆系统与 File SQL

## 1. 本次学习内容

Task05 主要包含两部分：

- P3：Agent 记忆系统设计
- I4：File SQL for AI Agent

本次实践重点完成：

1. 安装并体验 PowerContext 的基础记忆能力；
2. 验证显式 Memory 的写入与检索；
3. 使用 `read_csv()` 直接查询 CSV 文件；
4. 理解 File SQL 的适用场景、实现边界与工程问题。

---

## 2. P3：Agent 记忆系统理解

### 2.1 模型本身并不等于记忆系统

本节一个重要认识是：

> Agent 的长期记忆并不是模型天然具备的能力，而是模型之外的一套存储、提取、检索、更新和遗忘机制。

短期记忆主要服务当前对话，而长期记忆需要跨会话保存真正值得长期使用的信息。

长期记忆可以进一步理解为：

- Semantic Memory：事实、知识、稳定信息；
- Episodic Memory：过去发生过的事件和交互经历；
- Procedural Memory：规则、流程和做事方式。

这也意味着，并不是所有历史聊天内容都应该进入长期记忆。

真正重要的问题不是“能不能存”，而是：

> 什么值得存、什么时候写入、什么时候召回、什么时候应该遗忘。

---

## 3. Memory 的写入、检索与遗忘

### 3.1 写入

记忆可以有两种典型写入方式：

- 实时写入：交互过程中直接记录关键事实；
- 异步写入：会话结束后再进行提炼和归纳。

如果所有对话都直接进入长期记忆，会迅速产生大量噪声。

因此长期记忆更适合保存已经经过筛选的信息，例如：

- 长期稳定事实；
- 用户明确偏好；
- 已确认的重要决策；
- 可重复使用的方法和规则。

### 3.2 检索

长期记忆并不是简单按照时间顺序把旧聊天重新加载，而是根据当前问题检索相关内容。

其逻辑和 RAG 很相似：

```text
当前 Query
    ↓
检索相关历史信息
    ↓
选择最相关 Memory
    ↓
注入当前上下文

区别在于：
- RAG 更多检索外部知识；
- Memory 更多检索用户或 Agent 自身的历史状态和经验。
3.3 遗忘
本节让我意识到：
一个好的记忆系统不只是“记得更多”，还必须能够忘掉低价值和过期信息。

记忆可以综合考虑：
- 初始重要程度；
- 时间衰减；
- 最近是否被使用；
- 与当前问题的相关程度。
因此记忆系统本质上是一套动态的信息治理机制。
4. PowerContext 实践
4.1 实验环境
本次安装：
PowerContext 1.1.0
Python 3.12.10
Windows
SQLite

为了控制 Task05 的实验复杂度，本次选择：
运行范围：仅当前机器
存储：SQLite
能力：Basic Memory
Dashboard：开启
Agent 集成：暂不配置

没有配置 Generation API 和 Embedding API。
运行：
powercontext ready

返回：
Status: ready
database: ready
runtime: ready

继续检查：
powercontext capabilities

返回关键能力：
Artifact families: memory, topic-memory, experience, skill, handoff, profile, prompt
Memory extraction: disabled
Search modes: auto, fts
Context versions: powercontext.prepared-context.v1

这说明当前运行的是基础 Memory 模式：
- 支持显式 Memory；
- 支持 FTS 全文检索；
- 不启用自动 Memory Extraction；
- 不依赖额外模型 API。
5. 显式 Memory 写入与召回
本次写入了一条实验 Memory：
TASK05_MEMORY_MARKER：注规学习 Agent 的法规数据应保留法规版本与有效状态。

随后使用：
TASK05_MEMORY_MARKER

进行全文检索。
实际返回：
{
  "memory": {
    "family": "memory",
    "artifact_id": "memory",
    "revision": 1
  },
  "mode": "fts",
  "hits": [
    {
      "score": 0.01639344262295082,
      "matched_by": [
        "fts"
      ]
    }
  ]
}

经过 UTF-8 解码验证后，Memory 正文可以正常恢复为：
TASK05_MEMORY_MARKER：注规学习 Agent 的法规数据应保留法规版本与有效状态。

因此完成了：
显式 Memory 写入
    ↓
SQLite 持久化
    ↓
FTS 检索
    ↓
重新召回

这让我更直观地理解了：
“保存聊天记录”和“构建可检索长期记忆”是两个不同层次的问题。

6. PowerContext 实践中的一个问题：鉴权
PowerContext Server 开启 Dashboard 后启用了访问认证。
最初：
powercontext ready

可以正常返回，但：
powercontext capabilities

返回：
HTTP 401 (unauthorized)

原因是：
- /health/ready 属于公开健康检查；
- /v1/capabilities 属于需要认证的接口；
- 新开的 PowerShell 并不会自动读取 .env 中的 Server Token。
加载客户端 Token 后，powercontext capabilities 成功。
这个问题让我进一步理解了：
Server 正常运行和 Client 拥有访问权限是两个不同的问题。

7. I4：File SQL for AI Agent
7.1 为什么需要 File SQL
传统的数据文件分析通常需要：
识别格式
→ 建表
→ 导入数据
→ 查询
→ 删除临时表

但对于 Agent 临时分析用户上传的 CSV、JSONL 或 Parquet 文件，这套过程过重。
File SQL 的思路是：
直接把文件临时解释成关系，然后使用 SQL 查询。

例如：
SELECT *
FROM read_csv('orders.csv');

整个过程中不需要先创建持久表。
8. File SQL 实践数据
本次创建：
task05_orders.csv

内容：
order_id,customer_id,product,amount
1001,C001,规划原理教材,89
1002,C002,相关知识教材,96
1003,C001,法规教材,78
1004,C003,实务教材,108
1005,C002,真题集,66

9. seekdb 当前版本实测
首先尝试在当前课程使用的：
oceanbase/seekdb:latest

中直接执行：
SELECT *
FROM read_csv('/workspace/task05_orders.csv');

实际返回：
ERROR 1064 (42000):
You have an error in your SQL syntax
near '('/workspace/task05_orders.csv')'

因此在当前实际运行的 seekdb Docker 环境中，SQL Parser 尚未识别该 read_csv() 表函数语法。
这个实验说明：
课程中的 File SQL 接口代表目标设计能力，但具体函数是否可用仍然需要结合数据库实际版本验证，不能只根据教程假设产品已经实现。

10. 使用 DuckDB 完成 File SQL 实验
为了实际完成：
SELECT ... FROM read_csv(...)

流程，本次使用：
DuckDB 1.5.6

首先通过 Python csv.writer 重新生成标准 UTF-8 CSV，验证结果：
每行列数: [4, 4, 4, 4, 4, 4]

然后执行：
SELECT *
FROM read_csv('task05_orders.csv', header=true);

实际结果：
1001  C001  规划原理教材   89
1002  C002  相关知识教材   96
1003  C001  法规教材       78
1004  C003  实务教材      108
1005  C002  真题集         66

DuckDB 自动推断：
order_id     int64
customer_id  varchar
product      varchar
amount       int64

说明 CSV 文件可以直接成为 SQL 查询中的临时关系。
11. File SQL 聚合实验
进一步执行：
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount
FROM read_csv('task05_orders.csv', header=true)
GROUP BY customer_id
ORDER BY total_amount DESC;

实际结果：
customer_id  order_count  total_amount
C001         2            167
C002         2            162
C003         1            108

这说明 File SQL 不只是“读取 CSV”，文件关系还可以直接参与：
- SELECT
- GROUP BY
- COUNT
- SUM
- ORDER BY
等普通关系型 SQL 运算。
12. CSV 自动识别中的工程问题
第一次直接使用 DuckDB read_csv() 时，出现：
It was not possible to automatically detect the CSV parsing dialect

进一步指定参数后又出现：
The CSV Parser state machine reached an invalid state

最终使用 Python csv.writer 重新生成标准 UTF-8 CSV 后，读取成功。
这个过程让我认识到：
read_csv() 看起来只是一行 SQL，但实际仍然涉及编码、BOM、换行、Delimiter、Quote、Escape 和 Schema 推断等问题。

因此在 Agent 自动分析文件时，不应该把自动 Schema 和 CSV 方言识别视为绝对可靠。
更稳妥的 Agent 流程应该是：
发现文件
→ 检查格式
→ DESCRIBE / Schema 推断
→ 小样本验证
→ 正式查询
→ 导出与验证

而不是直接对未知文件执行复杂 SQL。
13. File SQL 的适用边界
通过本节学习，我认为 File SQL 特别适合：
临时文件
+ 一次性分析
+ 不需要事务
+ 不需要长期索引

而如果数据需要：
- 长期保存；
- 高频重复查询；
- 索引；
- 事务；
- 并发修改；
- 强一致性；
则更适合正式导入数据库表。
因此 File SQL 并不是替代数据库表，而是为 Agent 增加一种更低成本的临时数据访问方式。
14. Personal AI OS 的启发
P3 对我当前 Personal AI OS 也有比较直接的启发。
我目前更倾向于把长期信息分成不同层次：
长期稳定事实 / 偏好 / 重大决策
        ↓
长期 Memory

项目过程、阶段状态
        ↓
Project / Task Context

可复用知识
        ↓
Knowledge Base

原始文件与事实源
        ↓
权威数据源 / SSOT

这与本节“不是所有内容都应该进入长期 Memory”的思路是一致的。
Memory 更适合解决：
在未来正确的时机，重新找到过去真正重要的信息。

而不应该替代正式知识库、项目文件或权威事实源。
15. 本次总结
Task05 让我把两个此前比较抽象的概念真正联系了起来：
Memory
解决“过去哪些信息值得重新找到”

File SQL
解决“当前文件如何快速转化为可查询上下文”

二者实际上都在解决 Agent 的 Context 问题。
Memory 面向时间维度上的历史信息，File SQL 面向当前环境中的临时数据。
对 Agent 来说，真正重要的不只是拥有更多数据，而是：
能够在正确的时间，以正确的方式，访问正确的数据。

本次实验也让我进一步认识到，教程中的概念接口和实际产品版本之间可能存在差异，因此实践中必须通过真实运行结果确认能力边界，而不能仅依据文档假设功能已经可用。
参考资料
- Easy Data × AI：https://github.com/datawhalechina/easy-data-x-ai
- P3：Agent 记忆系统设计
- I4：File SQL for AI Agent
- PowerContext：https://github.com/oceanbase/powercontext
- DuckDB：https://duckdb.org/