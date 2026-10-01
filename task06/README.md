# Task 06｜Agentic RAG 实战与 AI Column 能力边界验证

> Datawhale《Easy Data × AI：构建知识与记忆驱动的 Agent》
> 状态：✅ 已完成

## 1｜本次学习内容

- D3｜Agentic RAG 实战
- I5｜AI 列 —— 模型驱动派生数据的自动维护
- d3_1 ～ d3_6 全链路实践
- Vector / Hybrid Retrieval 对比评测
- seekdb 检索精度、延迟与成本 Benchmark
- AI_EMBED 模型派生向量持久化实验
- AI Column DDL 当前环境兼容性验证

## 2｜D3-1：建立知识库

实际写入 19 个知识片段：

- release_notes：5
- error_codes：4
- financial：3
- best_practices：4
- api_reference：3

集合：

`d3_product_kb`

## 3｜D3-2：Agentic RAG

完成：

问题
→ Agent 判断是否需要检索
→ Tool Call
→ seekdb Hybrid Search
→ Tool Result
→ LLM 生成最终回答

四个测试中：

- 版本兼容问题：最终回答出现重复生成，未稳定给出完整结论
- E-4012：正确回答
- 2024 Q3 营收：正确回答
- 天气闲聊：回答表现符合“不需要检索”的预期

这让我认识到：

Agentic RAG 不只是“RAG + LLM”，而是让 Agent 动态决定是否检索、如何检索以及何时停止工具调用。

同时，检索链路成功并不意味着最终生成一定稳定，生产系统仍需：

- 最大工具轮数；
- Tool Call 校验；
- 超时；
- 重复调用防护；
- 最终答案校验。

## 4｜D3-3：纯向量 vs 增强检索

实际结果：

| 场景 | Vector | Enhanced |
|---|---|---|
| E-4012 | ❌ | ✅ |
| 2024 Q3 | ❌ | ❌ |
| OB-4.2.1 | ✅ | ✅ |
| DBMS_HYBRID_SEARCH | ❌ | ✅ |
| 查询性能 | ❌ | ❌ |

汇总：

- Vector：1/5
- Enhanced：3/5

实验说明：

错误码、函数名、版本号等精确标识符，仅依赖向量语义空间容易召回“很像但不是目标”的内容。

Hybrid Search 能引入精确关键词信号，但也不意味着一定正确。

例如 Q3 查询在增强检索下仍然返回 Q1，因此：

> 混合检索是增加检索信号，而不是自动获得正确答案。

## 5｜D3-4：生产工程实践

### Tool Description

本次实验中：

- 模糊描述：成功触发工具
- 清晰描述：成功触发工具

因此本次单次实验不能证明清晰描述一定提高工具调用率。

### top_k

实际验证：

- top_k=1 → 1 条
- top_k=3 → 3 条
- top_k=5 → 5 条
- top_k=8 → 8 条

### 增量更新

知识库：

19 → 20 条

说明 upsert 可以用于知识库增量维护，而不必每次整体重建。

## 6｜D3-5：Retrieval Evaluation

20 条评测集实际结果：

| 指标 | Vector | Hybrid |
|---|---:|---:|
| Gold Chunk Recall@K | 0.75 | 0.85 |
| Gold Chunk Precision@K | 0.275 | 0.316667 |
| Top-1 Reference Hit | 0.30 | 0.45 |
| Evidence Coverage@K | 0.75 | 0.85 |
| All Required Evidence@K | 0.65 | 0.80 |
| Stale Evidence Rate | 0.0625 | 0.075 |

两套评测：

`failures = {}`

我的理解：

Hybrid 提升了召回、Top-1 命中和证据完整性，但 stale evidence rate 略有增加。

所以生产级 RAG 不能只看 Recall，还应同时观察：

召回率 + 精度 + 证据完整性 + 新鲜度。

## 7｜D3-6：精度、延迟、成本三角实验

50 条可回答案例：

| 指标 | Vector | Hybrid |
|---|---:|---:|
| Hit@1 | 0.44 | 0.74 |
| Hit@3 | 0.74 | 0.98 |
| MRR | 0.60 | 0.85 |
| P50 | 152.6572 ms | 115.3807 ms |
| P95 | 168.2597 ms | 184.9929 ms |
| Avg Context Token | 103.48 | 101.82 |
| 示例千次上下文成本 | CNY 0.1035 | CNY 0.1018 |

相对于 Vector：

- Hit@1：+30 个百分点
- P95：+9.9%
- Token / Query：-1.6%

这说明：

> 检索方案选择本质上是 Precision / Latency / Cost 三角权衡。

## 8｜I5：AI Column

### 8.1 当前环境

seekdb：

`5.7.25-OceanBase seekdb-v1.4.0.0`

Docker：

`oceanbase/seekdb:latest`

已注册：

- Model：task04_embed_model
- Type：DENSE_EMBEDDING
- Physical Model：BAAI/bge-m3
- Provider：openai
- Endpoint：SiliconFlow Embeddings

### 8.2 AI_EMBED 实测

执行：

```sql
SELECT JSON_LENGTH(
  AI_EMBED(
    'task04_embed_model',
    'Agentic RAG combines agent decision making with knowledge retrieval.'
  )
);
```

实际：

`1024`

说明数据库可以通过 SQL 直接调用外部 Embedding 模型。

### 8.3 模型派生向量持久化

建立：

```sql
content VARCHAR(1000),
embedding VECTOR(1024)
```

然后：

```sql
INSERT ... AI_EMBED(...)
```

实际：

- `embedding_is_null = 0`
- `dimensions = 1024`

完成了：

文本  
→ AI_EMBED  
→ SiliconFlow  
→ BAAI/bge-m3  
→ 1024 维向量  
→ seekdb 持久化

### 8.4 为什么需要 AI Column

只修改：

```sql
UPDATE ... SET content='The source content has changed.'
```

之后：

- content 已变化
- embedding 仍然存在
- dimensions 仍然是 1024

普通列不会知道 embedding 已经属于旧版本文本。

因此应用层必须自行维护：

- 依赖关系
- 失效
- 重算
- 重试
- 版本
- 并发一致性

AI Column 要解决的正是这套问题。

### 8.5 当前版本能力边界

课程稿中的：

```sql
VECTOR(1024) AI COLUMN (
  AI_EMBED(...)
)
```

在本次实测环境：

`seekdb-v1.4.0.0`

且已经确认运行镜像与 2026-10-01 当时的：

`oceanbase/seekdb:latest`

一致。

实际执行返回：

`ERROR 1064`

因此本次不声称已经成功创建 AI Column。

这一实践也提醒我：

> 课程概念、文档语法和实际发布版本之间可能存在时间差，实验记录还是要以真实运行结果为准。

## 9｜本阶段核心理解

### 9.1 Agentic RAG

传统 RAG：

固定流程  
→ 每个问题都检索  
→ 再生成

Agentic RAG：

Agent  
→ 判断是否检索  
→ 选择工具  
→ 获取证据  
→ 判断是否继续  
→ 最终回答

### 9.2 Retrieval

不能把 Vector Search 当成唯一答案。

真实知识系统通常需要：

- Vector Search
- Full-text Search
- Metadata Filter
- Hybrid Fusion
- Evaluation

### 9.3 AI Native 数据系统

AI 不仅可以位于应用层。

它还可以逐步进入：

SQL Function  
→ 数据派生  
→ 检索  
→ 索引  
→ 数据生命周期

但 AI 派生数据不能自动成为事实源。

在我的 Personal AI OS 中，我会继续坚持：

> 原始事实 / 权威数据源  
> 高于  
> AI 派生结果。

AI 生成的摘要、标签、Embedding 或记忆，本质上仍属于派生数据，需要保留来源、版本和生成条件。

## 10｜参考资料

- Datawhale Easy Data × AI
- D3：Agentic RAG 实战
- I5：AI 列 —— 模型驱动派生数据的自动维护
- seekdb
- SiliconFlow