# Task 04｜统一 AI Native 数据层与 SQL × AI Functions

> Datawhale《Easy Data × AI：构建知识与记忆驱动的 Agent》学习记录  
> 状态：✅ 已完成

## 1｜本次学习内容

Task 04 主要学习和实践：

- D2｜AI 应用的数据层
- I3｜SQL × AI —— AI Functions 的设计与执行
- `d2_1`～`d2_5` 完整代码实践
- seekdb Hybrid Search 实验
- Chunking 策略对比实验
- SQL × AI Function 真机调用

本阶段是在 Task 03 对 RAG 和向量数据库建立基本理解后，进一步进入真正的数据层工程实践：

> 数据如何切分  
> → 如何向量化  
> → 如何存储  
> → 如何查询  
> → 如何进行混合检索  
> → 如何比较不同 Chunking 策略  
> → 如何直接在 SQL 数据链路中调用 AI 模型。

本次继续以“注册城乡规划师学习 Agent / App”作为主要个人实践映射案例。

---

## 2｜D2：AI 应用的数据层

### 2.1 我对 AI Native 数据层的新理解

学习 D2 前，我比较容易把 AI 应用的数据层理解为：

> 给大模型准备一个向量数据库。

完成本阶段后，我认为更准确的理解是：

> AI 应用的数据层不是单纯存储数据，而是决定 Agent 能获得什么信息、如何找到这些信息，以及不同类型信息如何组合。

真实 AI 应用通常同时存在：

- 语义相似问题；
- 精确关键词；
- 错误码；
- 法规条款；
- 产品版本；
- 时间；
- 权限；
- 状态；
- 分类；

因此不能只依赖单一 Vector Search。

更完整的数据层需要同时考虑：

> Vector Search  
> + Full-text Search  
> + Metadata / Scalar Filter  
> + 必要的结构化查询  
> + Fusion / Reranking

---

## 3｜`d2_1`：数据写入

执行：

```powershell
.\.venv\Scripts\python.exe D2\d2_1_ingest.py
```

实际结果：

```text
>>> 已删除旧的集合：d2_knowledge_base
>>> 原始文档数：8
>>> 切分后片段数：8
>>> seekdb 中实际存储条数：8
✅ d2_1 写入完成，可继续运行 d2_2 / d2_3 / d2_4。
```

这一实验完成了一个最小的数据入库链路：

> 原始文档  
> → Chunking  
> → Metadata  
> → Embedding / 索引  
> → seekdb

本次示例只有 8 条较短文档，所以切分后仍为 8 个片段。

真实知识库中的长教材、法规和课程材料则需要进一步设计：

- Chunk 大小；
- Overlap；
- 语义边界；
- 元数据；
- 原始来源；
- 版本；
- 权限。

---

## 4｜`d2_2`：纯向量搜索

执行：

```
.\.venv\Scripts\python.exe D2\d2_2_vector_search.py
```

### 4.1 查询一：怎么设计用户权限

知识库中实际上存在：

> 访问控制架构设计：基于 RBAC 实现用户权限管理，并按最小权限原则分配角色。

但纯向量搜索实际 Top 3 为：

```
[1] 连接池配置
[2] 数据备份与恢复
[3] 数据库查询性能优化指南
```

程序最终判断：

```
⚠️ 本次结果未命中访问控制/RBAC，不能断言语义检索成功。
```

这个实验非常重要，因为它说明：

> 使用 Vector Search 并不意味着一定能够正确完成语义召回。

检索质量还会受到：

- Embedding 模型；
- 数据规模；
- 文档表达；
- Chunk；
- Top-K；
- 数据分布；
- 检索实现；

等因素影响。

---

### 4.2 查询二：错误码 E-4012

查询：

> 错误码 E-4012 的解决方案

实际结果：

```
[1] E-4012 数据库连接超时
[2] E-4013 认证失败
[3] E-4011 连接被拒绝
```

程序提示：

```
✅ 本次向量搜索第一名恰好是 E-4012；实际排名仍可能受模型影响。
```

这次虽然成功，但不能因此得出：

> 向量搜索适合所有精确标识符查询。

因为：

`E-4011 / E-4012 / E-4013`

在语义空间中高度相似。

对于：

- 错误码；
- 法规条款；
- 版本号；
- 型号；
- API 参数；
- 文件编号；

仍然需要 Full-text Search 等精确检索能力。

---

## 5｜`d2_3`：Hybrid Search

执行：

```
.\.venv\Scripts\python.exe D2\d2_3_hybrid_search.py
```

本次实验包含三种场景。

### 5.1 精确编号

查询：

> E-4012 的解决方案

结果：

```
[1] E-4012
[2] E-4013
[3] E-4011
```

程序判断：

```
✅ E-4012 位于混合搜索第一名。
```

---

### 5.2 语义理解

查询：

> 怎么设计用户权限

混合搜索实际返回：

```
[1] 访问控制架构设计：基于 RBAC 实现用户权限管理
[2] 连接池配置
[3] 数据备份与恢复
```

程序判断：

```
✅ 结果中找到了访问控制/RBAC 相关文档。
```

这与 `d2_2` 形成了非常清晰的对比：

```
纯向量搜索
→ 未命中 RBAC

混合搜索
→ RBAC 排名第一
```

---

### 5.3 Metadata 版本过滤

查询：

> 性能优化

同时限制：

```
version = 4.2
```

结果全部满足：

```
version=4.2
```

程序判断：

```
✅ 返回结果均满足 version=4.2。
```

这让我第一次从实际代码中看到三种检索能力协同：

- 语义检索；
- 精确全文信号；
- Metadata Filter。

而不是所有问题都交给向量空间解决。

---

## 6｜`d2_4`：纯向量搜索 vs Hybrid Search

执行：

```
.\.venv\Scripts\python.exe D2\d2_4_compare.py
```

这一实验是本次 Task 04 中最直观的一组验证。

### 6.1 E-4012

纯向量和混合搜索本次都把：

> E-4012

放在第一名。

因此这一个 Query 本身不能证明混合搜索一定优于纯向量。

---

### 6.2 用户权限

查询：

> 怎么设计用户权限

纯向量搜索：

```
1. 连接池配置
2. 数据备份与恢复
3. 数据库查询性能优化
```

混合搜索：

```
1. 访问控制架构设计 / RBAC
2. 连接池配置
3. 数据备份与恢复
```

目标文档从：

> 没有进入 Top 3

变成：

> 排名第一。

---

### 6.3 数据库性能优化

查询：

> 数据库性能优化

纯向量搜索中：

> 数据库查询性能优化指南排在第 3。

混合搜索中：

> 数据库查询性能优化指南排在第 1。

---

### 6.4 实验结论

在本次课程数据、当前 Embedding 模型和查询条件下：

> Hybrid Search 明显改善了两类纯向量检索的排序偏差。

因此我对“混合搜索”的理解从：

> 理论上应该更好

转变成了：

> 同样的数据和 Query，仅改变检索策略，实际排序质量就可能发生明显变化。

同时也不能把这个小规模实验泛化为：

> 混合搜索在所有数据、所有 Query 上一定更好。

生产系统仍然需要：

- 真实 Query；
- Ground Truth；
- Recall\@K；
- MRR；
- Precision\@K；
- nDCG；

等评测验证。

---

## 7｜`d2_5`：Chunking 策略对比

执行：

```
.\.venv\Scripts\python.exe D2\d2_5_chunking_compare.py
```

本次检测到了：

```
SILICONFLOW_API_KEY
```

因此四种策略全部参与实验。

实际结果：

| Chunking 策略 | 块数 | 平均长度  | Recall@3 |
| ----------- | -- | ----- | --------- |
| 固定 overlap  | 5  | 186 字 | 100%      |
| 动态 overlap  | 6  | 185 字 | 80%       |
| 父子 chunk    | 9  | 104 字 | 60%       |
| 语义分块        | 2  | 396 字 | 60%       |

---

### 7.1 固定 overlap

本次：

> Recall\@3 = 100%

说明在当前这份小型结构化运维文档和 5 个测试 Query 中：

> 简单的固定 overlap 反而效果最好。

---

### 7.2 动态 overlap

本次：

> Recall\@3 = 80%

动态调整边界并没有在当前实验里超过固定 overlap。

---

### 7.3 父子 Chunk

本次：

> Recall\@3 = 60%

但是父子 Chunk 的价值不能只看当前 Recall：

> 它的核心优势是“小块用于定位，大块用于给 LLM 提供完整上下文”。

因此在跨段理解和生成完整性方面，可能仍有价值。

---

### 7.4 语义分块

本次：

> 只有 2 个 Chunk\
> 平均 396 字\
> Recall\@3 = 60%

说明当前语义分块把多个内容合并成了较大的语义块。

---

### 7.5 我对 Chunking 的新理解

这个实验给我的最大启发不是：

> 固定 overlap 是最优算法。

而是：

> 更复杂的 Chunking 方法不天然优于简单方法。

当前实验只有：

- 一份小型文档；
- 5 个 Query；
- 当前 Embedding 模型；
- Recall\@3 一个核心指标。

因此真正的策略选择应该是：

> 拿自己的真实文档 + 真实问题做评测。

这对后续构建注规学习 Agent 很重要，因为：

- 教材；
- 法规；
- 真题；
- 网课转写；

四种数据的结构完全不同，未来可能需要采用不同 Chunking 策略，而不是统一切法。

---

## 8｜I3：SQL × AI —— AI Functions

### 8.1 AI Function 和普通 SQL Function 的区别

普通 SQL 函数例如：

```
UPPER(title)
```

通常在数据库内部直接执行。

但：

```
AI_EMBED(...)
AI_RERANK(...)
AI_COMPLETE(...)
```

虽然语法上看起来像 SQL Function，本质上可能是：

> 数据库发起的远程 AI 网络调用。

因此会额外带来：

- 网络延迟；
- 限流；
- 超时；
- Provider 兼容；
- Token / API 成本；
- 重试；
- 非确定性；
- 权限；
- 数据出域风险。

这是本阶段最重要的心智模型之一。

---

## 9｜I3 四类 AI Function

官方课程介绍了四种核心函数。

| Function      | 主要作用          | 是否调用外部模型 |
| ------------- | ------------- | -------- |
| `AI_EMBED`    | 文本转 Embedding | 是        |
| `AI_RERANK`   | 对候选结果重新排序     | 是        |
| `AI_COMPLETE` | 调用生成模型        | 是        |
| `AI_PROMPT`   | 组织 Prompt     | 否        |

本次真机实验实际验证了：

- `AI_PROMPT`
- `AI_EMBED`

`AI_RERANK` 和 `AI_COMPLETE` 本阶段主要完成原理学习，没有虚构为已经实际运行。

---

## 10｜`AI_PROMPT` 真机实验

执行：

```
SELECT AI_PROMPT(
  '问题：{0}',
  '什么是RAG'
) AS prompt;
```

实际返回：

```
{
  "args": ["什么是RAG"],
  "template": "问题：{0}"
}
```

说明：

> `AI_PROMPT` 本质是 Prompt 模板和参数的结构化组装。

它本身：

> 不会调用外部模型。

这也与课程中的设计定位一致。

---

## 11｜注册 AI 逻辑模型与 Endpoint

本次在 seekdb 中注册：

```
逻辑模型：
task04_embed_model
```

类型：

```
dense_embedding
```

实际模型：

```
BAAI/bge-m3
```

同时注册模型 Endpoint，指向 SiliconFlow OpenAI-compatible Embedding API。

API Key 由本地 `.env` 读取，没有：

- 输出到终端；
- 写入 README；
- 上传 GitHub。

这一实践让我理解了为什么数据库要把：

> 逻辑 Model

与：

> Endpoint / Provider / API Key / 物理模型

分开。

业务 SQL 可以只引用：

```
task04_embed_model
```

而不必在每一条查询中硬编码：

- URL；
- Provider；
- API Key。

---

## 12｜`AI_EMBED` 真机实验

实际执行：

```
SELECT JSON_LENGTH(
  AI_EMBED(
    'task04_embed_model',
    '如何理解国土空间规划中的三区三线'
  )
) AS embedding_dim;
```

实际结果：

```
embedding_dim
1024
```

这意味着实际完成了：

```
SQL
↓
AI_EMBED
↓
seekdb 解析逻辑模型
↓
Model Endpoint
↓
OpenAI Compatible Protocol
↓
SiliconFlow
↓
BAAI/bge-m3
↓
返回 Embedding
↓
seekdb
↓
JSON_LENGTH
↓
1024
```

这是我第一次实际通过：

> 数据库 SQL

直接调用外部 AI 模型。

与之前 Python 代码主动调用模型相比，本次模型能力已经进入：

> SQL 数据处理链路。

---

## 13｜Tool Use 与 AI Function 的区别

Task 02 中的 Tool Use：

```
用户
↓
LLM
↓
判断是否调用 Tool
↓
Python / 外部代码执行
↓
Tool Result
↓
LLM继续推理
```

Task 04 中的 AI Function：

```
SQL
↓
数据库执行 AI Function
↓
数据库解析模型和 Endpoint
↓
外部模型
↓
模型结果返回数据库
↓
继续参加 SQL 计算
```

因此：

> Tool Use 解决的是 Agent 如何主动调用外部能力。

而：

> AI Functions 解决的是 AI 能力如何进入数据处理与 SQL 执行链路。

---

## 14｜AI Functions 的工程边界

### 14.1 一条 SQL 不等于一次模型请求

例如：

```
SELECT AI_COMPLETE('model', content)
FROM documents;
```

如果过滤后存在：

> 1000 行

那么可能接近：

> 1000 次模型调用。

所以真正的模型成本取决于：

> AI Function 的实际求值次数

而不是：

> SQL 语句数量。

---

### 14.2 先过滤，再调用 AI

相比：

```
SELECT AI_COMPLETE('model', content)
FROM documents;
```

更合理的是先：

- Tenant Filter；
- Status Filter；
- NULL Filter；
- Limit；

然后只让 AI Function 处理真正需要的数据。

这与 RAG 中：

> 先缩小 Candidate，再做昂贵 Rerank

是同一类工程思想。

---

### 14.3 数据库事务不能撤销 AI 推理

假设：

```
START TRANSACTION
↓
AI_COMPLETE
↓
模型请求已经发生
↓
ROLLBACK
```

数据库可以回滚：

> 数据写入。

但不能回滚：

- HTTP 请求；
- 已完成推理；
- API Token；
- 已产生费用。

因此：

> AI Function 不能被当成普通确定性本地数据库函数。

---

### 14.4 更合理的是两阶段处理

例如：

```
阶段 A
短事务选择数据
→ 固化输入
→ 记录任务状态
→ COMMIT

阶段 B
事务外调用 AI
→ 验证结果
→ 短事务写回
```

这样更容易处理：

- Retry；
- Timeout；
- Cost；
- Checkpoint；
- Failure Recovery；
- Observability。

---

## 15｜哪些任务适合 SQL × AI

更适合的任务：

- 单次 Query Embedding；
- 有限候选集的 Rerank；
- 小规模分类；
- 小规模摘要；
- 信息抽取；
- 紧贴数据库上下文的 AI 计算。

而：

- 长时间 Agent；
- 多轮 Tool Calling；
- 大规模异步批处理；
- 流式生成；
- 多模态复杂交互；
- 需要人工审批的复杂业务流；

通常更适合应用层或 Workflow。

我目前可以用一句话判断：

> 越靠近数据、数据集合越有限、输入输出越结构化、失败边界越清楚，就越适合 SQL × AI。

---

## 16｜映射到注规学习 Agent

Task 04 对注规学习 Agent 的直接启发，是开始把“知识库”进一步拆成真正的数据处理能力。

未来可能形成：

```
注规教材 / 法规 / 真题 / 网课 / 错题
                ↓
            数据解析
                ↓
             Chunking
                ↓
              Embed
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
 Vector      Full-text    Metadata
 Search       Search       Filter
    └───────────┼───────────┘
                ↓
              RRF
                ↓
             Rerank
                ↓
            Evidence
                ↓
              LLM
                ↓
          答案 + 来源
```

---

### 16.1 法规尤其需要混合检索

例如：

> 《城乡规划法》第四十条规定了什么？

不能只使用：

> Vector Search

因为：

- 第三十九条；
- 第四十条；
- 第四十一条；

在语义上都属于规划法规条款。

更合理的是：

```
全文检索
→ 精确锁定“第四十条”

Metadata
→ 过滤现行有效版本

Vector
→ 补充相关语义内容

Rerank
→ 排序最终证据
```

---

### 16.2 不同资料可能使用不同 Chunking

注规教材：

> 可能更适合章节 / 标题边界 + overlap。

法规：

> 更适合按条、款、项进行结构化切分。

真题：

> 更适合“一题 + 选项 + 答案 + 解析 + 知识点”作为基本数据单元。

网课：

> 可能需要按时间段 + 语义主题进行分块。

因此本次 `d2_5` 的真正意义不是选择“100% Recall 的 fixed overlap”直接应用到所有资料，而是建立：

> 不同数据类型应分别评测 Chunking 策略

的方法。

---

## 17｜Task 04 阶段总结

Task 03 让我理解：

> RAG 不只是向量数据库。

Task 04 则进一步让我真正从代码层看到：

> 为什么真实 AI 数据层需要 Vector、Full-text、Metadata 和 Hybrid Search 协同工作。

这次最有价值的真实实验是：

> “怎么设计用户权限”在纯向量搜索中完全没有召回 RBAC 文档，但 Hybrid Search 直接把 RBAC 文档提升到了第一名。

说明：

> 数据存在，并不意味着 AI 一定能找到；检索策略本身会直接决定最终 Agent 能看到什么。

Chunking 实验也让我看到：

> 更复杂的算法不天然更好。

在当前小型测试集里：

> 固定 overlap 的 Recall\@3 反而达到 100%。

因此真正重要的是：

> 在自己的真实数据和 Query 上评测。

I3 则进一步把我的理解从：

> AI 在应用代码里访问数据库

扩展到了：

> 数据库本身也可以通过 AI Functions 调用模型。

通过 `AI_EMBED` 实验，seekdb 成功从 SQL 中调用 SiliconFlow 的 `BAAI/bge-m3`，并返回 1024 维向量。

同时我也开始理解 AI Functions 的工程边界：

- 一条 SQL 可能产生大量模型请求；
- 外部模型调用不能被数据库事务回滚；
- AI 结果必须考虑失败、重试和成本；
- Prompt 输出不能未经验证直接进入正式数据；
- 不是所有 AI 任务都应该塞进数据库。

到目前为止，我对一个 Agent 的数据链路已经开始形成更完整的认识：

> Agent 的能力不只来自模型，而来自模型、检索、数据库、工具、状态和可靠工程边界共同作用。

---

## 参考资料

- Datawhale Easy Data × AI 官方仓库：\
  [https://github.com/datawhalechina/easy-data-x-ai](https://github.com/datawhalechina/easy-data-x-ai?utm_source=chatgpt.com)
- 在线课程：\
  [https://datawhalechina.github.io/easy-data-x-ai](https://datawhalechina.github.io/easy-data-x-ai?utm_source=chatgpt.com)
- D2｜AI 应用的数据层：\
  [https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/dev/D2%20%E8%AF%BE%E7%A8%8B%E7%A8%BF%EF%BC%9AAI%20%E5%BA%94%E7%94%A8%E7%9A%84%E6%95%B0%E6%8D%AE%E5%B1%82.md](https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/dev/D2%20%E8%AF%BE%E7%A8%8B%E7%A8%BF%EF%BC%9AAI%20%E5%BA%94%E7%94%A8%E7%9A%84%E6%95%B0%E6%8D%AE%E5%B1%82.md)
- I3｜SQL × AI —— AI Functions 的设计与执行：\
  [https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/industry/I3%20%E8%AF%BE%E7%A8%8B%E7%A8%BF%EF%BC%9ASQL%20%C3%97%20AI%20%E2%80%94%E2%80%94%20AI%20Functions%20%E7%9A%84%E8%AE%BE%E8%AE%A1%E4%B8%8E%E6%89%A7%E8%A1%8C.md](https://github.com/datawhalechina/easy-data-x-ai/blob/main/docs/industry/I3%20%E8%AF%BE%E7%A8%8B%E7%A8%BF%EF%BC%9ASQL%20%C3%97%20AI%20%E2%80%94%E2%80%94%20AI%20Functions%20%E7%9A%84%E8%AE%BE%E8%AE%A1%E4%B8%8E%E6%89%A7%E8%A1%8C.md)
- Task 安排：\
  [https://my.feishu.cn/wiki/HvQuwKiSEi0mNBkGzjBcJaldnrd](https://my.feishu.cn/wiki/HvQuwKiSEi0mNBkGzjBcJaldnrd)
