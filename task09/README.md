# Task09｜Agent 三层质量度量、课程总结与 PowerContext 测评实践

> Datawhale《Easy Data × AI：构建知识与记忆驱动的 Agent》  
> 学习内容：P5《综合案例与度量》、D5《课程总结》、I8《案例场景和测评构建》  
> 记录日期：2026-10-11  
> 实践状态：**P5 主要实验完成；D5 已结合 Task06/Task08 复盘；I8 Harbor 验收成功，LoCoMo Plus 仅完成 query-only 有效评分，Memory 组存在待解决的 HTTP 400 故障。**

## 1｜本次学习的目标与完成概况

这次 Task09 我不再只追求「代码能跑」，而是尝试回答三个更接近真实 Agent 产品的问题：

1. **P5：** Agent 的数据质量、回答质量和业务结果分别如何度量？在什么业务条件下有投资回报？
2. **D5：** D1 Tool Use、D2 数据层、D3 Agentic RAG、D4 Memory 如何组成完整系统？我以前的实验说明了什么？
3. **I8：** 如何固定数据版本与评分协议，用 Harbor 检查上下文链路，再通过 LoCoMo Plus 对比无记忆和有记忆的效果？失败时怎样保留可复查证据？

### 1.1 实验清单

| 模块 | 实验 | 实际状态 |
| --- | --- | --- |
| P5 | 30 条离线 Knowledge Agent 评测 | ✅ 完成 |
| P5 | 三情景、首年 12 个月 ROI 测算 | ✅ 完成 |
| P5 | Python unittest | ✅ 38/38 通过 |
| P5 | Docker Agent / Prometheus / Grafana | ✅ 容器启动，Agent 健康，Prometheus 抓取正常，Dashboard 已加载 |
| P5 | Demo Traffic | ✅ 两轮各 100 条，共发送 200 条 |
| D5 | D1–D4 串联和既有实验复盘 | ✅ 完成 |
| D5 | Vector 与 Hybrid 对照 | ✅ 复用 Task06 已有真实数据 |
| D5 | PowerMem 跨进程记忆 | ✅ 复用 Task08 已有真实数据 |
| I8 | Harbor E2E 和离线重新评分 | ✅ 完成 |
| I8 | LoCoMo Plus 数据检查、Dry-run | ✅ 完成 |
| I8 | LoCoMo Plus query-only | ✅ 两题均生成、完成 Judge 评分 |
| I8 | LoCoMo Plus memory | ⚠️ 两题均在首个历史会话的 Memory 提取阶段失败，未评分 |

**口径说明：** 本次 P5 使用课程模拟数据；I8 LoCoMo Plus 是两题 SUBSET 诊断，不是完整公开榜单成绩。运行成功、模型答错、基础设施失败必须分别记录。

---

## 2｜P5：从离线评测到 Agent ROI

### 2.1 环境准备

在 WSL2 Ubuntu 中获取官方课程仓库：

~~~bash
cd ~
git clone --depth 1 https://github.com/datawhalechina/easy-data-x-ai.git easy-data-x-ai-course
cd ~/easy-data-x-ai-course/code/P5
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
~~~

实践目录为 **/home/joe/easy-data-x-ai-course/code/P5**。课程自带 Agent 和样本可以离线运行，不依赖真实 LLM API。

### 2.2 30 条离线评测

运行：

~~~bash
.venv/bin/python -m app.evaluation.run_eval
cat outputs/evaluation_report.md
~~~

实际生成：

- outputs/evaluation_report.json
- outputs/evaluation_report.md

**实际结果（30 条课程模拟样本）：**

| 质量层 | 指标 | 结果 |
| --- | --- | ---: |
| 数据层 | 知识覆盖率 | 82.76% |
| 数据层 | 检索命中率 | 95.83% |
| 数据层 / 运行诊断 | 检索故障率 | 3.33% |
| 模型层 | 回答准确率 | 96.67% |
| 模型层 | 幻觉率 | 3.33% |
| 业务层 | 任务成功率 | 73.33% |
| 业务层 | 转人工率 | 23.33% |
| 业务层 | 行为一致率 | 100.00% |
| 运行层 | 工具成功率 | 80.00% |
| 运行层 | 平均延迟 | 108.67 ms |
| 运行层 | 平均 Token 使用量 | 23.53 |

30 条样本中，**22 条任务成功、7 条转人工、1 条未成功且没有转人工**。值得关注的具体失败：

- general-008、missing-001 至 missing-004：知识没有命中或缺失，最终转人工；
- tool-005：工具任务未完成，转人工；
- exception-001：异常后转人工；
- exception-002：产生错误答案和幻觉，且没有转人工，是更值得优先处理的异常处置问题。

**我的判断：** 回答准确率与任务成功率不能混为一谈。回答正确也可能只是正确地转人工，并没有独立完成业务。该案例下一轮优先补齐高频知识、完善失败降级和转人工逻辑，而不是直接花钱更换更大的模型。

### 2.3 ROI：保守、基准、乐观三个情景

运行：

~~~bash
.venv/bin/python -m app.roi.calculator --config config/roi_scenarios.yaml --output-dir outputs
cat outputs/roi_report.md
~~~

生成 roi_report.md、roi_report.json、scenario_comparison.csv。计算周期 **12 个月**，单位 **CNY**。

| 情景 | 首年总成本 | 首年总收益 | 净收益 | 首年 ROI | 回收期 | 盈亏平衡月任务量 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| conservative | ¥14,900 | ¥11,256 | -¥3,644 | -24.46% | 107.89 月 | 115 |
| base | ¥13,600 | ¥22,800 | +¥9,200 | 67.65% | 3.64 月 | 52 |
| optimistic | ¥13,648 | ¥39,432 | +¥25,784 | 188.92% | 1.61 月 | 37 |

基本公式：

> 首年总成本 = 初始投入 + 12 ×（月固定成本 + 月可变成本）  
> 首年净收益 = 首年总收益 − 首年总成本  
> ROI = 首年净收益 ÷ 首年总成本 × 100%

一个让我印象深刻的细节是：保守情景**每月净收益虽然有 ¥38**，但初始投入 ¥4,100，所以首年仍然为负：

> 12 × 38 − 4,100 = -3,644 元。

因此，不能以「每个月开始赚钱」代替完整投资回报分析。基准情景的 100 个任务/月高于盈亏平衡量 52，保守情景的 80 个任务/月却低于所需的 115。

**限制：** 这些数字是课程 YAML 内的模拟经营假设，不能直接作为我的 Personal AI OS、文旅服务或其它实际业务的收入预测。真实应用必须重新收集任务量、转人工率、人工处理成本、风险损失、模型/工具费用，并避免收益重复计算。

### 2.4 自动化测试：38/38 通过

运行：

~~~bash
.venv/bin/python -m unittest discover -s tests -v
~~~

实际结果：

~~~text
Ran 38 tests in 0.261s

OK
~~~

覆盖 Evaluation、ROI、Knowledge Agent 行为、指标计数、Prometheus/Dashboard 配置、模拟流量、LangSmith 开关与敏感标签限制等。**通过单元测试不代表整个线上监控链路已经运行，需要继续部署和验证。**

### 2.5 Docker Compose：Agent + Prometheus + Grafana

WSL Ubuntu 已正确连接 Docker Desktop，实际使用：

~~~bash
cd ~/easy-data-x-ai-course/code/P5
read -rsp "Grafana password: " GRAFANA_ADMIN_PASSWORD
echo
export GRAFANA_ADMIN_PASSWORD
docker compose up -d --build
docker compose ps
~~~

本次成功启动：

| 服务 | 本地端口 | 验证结果 |
| --- | --- | --- |
| p5-agent-1 | 127.0.0.1:8000 | Up (healthy)，/health 返回 status=ok |
| p5-prometheus-1 | 127.0.0.1:9090 | Up，目标 p5-knowledge-agent 状态 up，lastError=none |
| p5-grafana-1 | 127.0.0.1:3000 | Up，自动加载 P5 Agent / 三层质量与运行监控 Dashboard |

验证命令：

~~~bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:9090/api/v1/targets
~~~

Grafana 界面已看到 Total Requests=100、模拟 Total Cost 约 0.0469 CNY。首次截图中部分增量/速率曲线尚为空白；后续已确认 Prometheus Target 为 up，**但没有最终截图证明所有面板的曲线都已正常显示，故不作该项声明**。

### 2.6 生成两轮模拟流量

运行两次：

~~~bash
.venv/bin/python -m app.observability.generate_traffic --count 100
~~~

两轮各自返回相同的七类模拟场景分布：

| 单轮场景 | 数量 |
| --- | ---: |
| success | 15 |
| retrieval_miss | 15 |
| missing_knowledge | 14 |
| retrieval_failure | 14 |
| hallucination | 14 |
| tool_failure | 14 |
| handoff | 14 |
| **每轮合计** | **100** |

合计 **发送 200 条模拟请求**。第一轮 /metrics 实际观测值包括：

~~~text
agent_requests_total{agent_version="mock-v1",environment="docker",status="success"} 100
agent_knowledge_available_total 44
agent_knowledge_evaluated_total 86
agent_retrieval_total 44
agent_retrieval_hit_total 29
agent_retrieval_errors_total 14
agent_token_usage_total 2344
agent_cost_total 0.04688
~~~

以上去掉了部分 label 以方便阅读，完整原文在本地 Prometheus 指标响应中。按第一轮计数：知识覆盖率 44/86≈51.16%，检索命中率 29/44≈65.91%，检索故障率 14/100=14%。

**注意：** API 请求状态 100% success，不等于业务任务 100% 成功；这 100 条流量故意平均注入多种故障，样本分布与前面的 30 条离线评测不同，不能把两组指标直接相减说成「模型退化」。监控的 0.04688 CNY 是模拟成本，非真实 SiliconFlow 账单。

实验结束后可在课程目录执行 docker compose down 清理容器；本次 README 不声称已经执行清理。

### 2.7 P5 最终认识

我现在更倾向于用「**数据层 → 模型层 → 业务层**」定位质量原因，用「**运行监控**」补充系统可靠性，用「**ROI**」判断投入是否值得。

运行层不是独立的第四个质量归因层。只有当诊断指标真正影响独立任务完成、转人工或风险等业务结果时，才能进一步换算收益；不能将召回率、准确率、满意度各自折算收入后重复相加。

---

## 3｜D5：D1–D4 课程总结与真实实验复盘

D5 不引入新的技术组件，目的是把我此前完成的 Tool Use、seekDB、Agentic RAG 和 Memory 实践联系起来。

### 3.1 四项能力在系统中的位置

| 课程 | 解决的问题 | 对应工程能力 |
| --- | --- | --- |
| D1 Tool Use | Agent 如何执行外部操作？ | Tool Call、行动循环、结果反馈与停止条件 |
| D2 seekDB | Agent 的信息放在哪里、如何检索？ | 向量、全文、结构化字段与混合检索 |
| D3 Agentic RAG | 如何选择证据并根据证据作答？ | 检索工具、结果校验、引用与生成 |
| D4 Memory | 如何跨会话保留、找回并维护信息？ | Memory 提取、持久化、Scope、版本与清理 |

我理解的主线是：

> 用户任务 → Agent 决策 → 工具调用 → 数据 / Memory 检索 → 上下文装配 → 模型回答或执行 → 任务结果与评测。

Agent 不是单纯「更会说话」的大模型，而是模型与工具、数据、状态管理和执行控制组成的系统。

### 3.2 D3：复用 Task06 中真实的 Vector / Hybrid 对照

来源：本仓库 [task06/README.md](../task06/README.md)。

第一组 5 条专有名词/精确查询，纯向量 **1/5**，增强检索 **3/5**；其中 2024 Q3 查询即使在增强检索下仍然命中 Q1，说明 Hybrid 不是万能修复。

第二组 20 条检索评测：

| 指标 | Vector | Hybrid |
| --- | ---: | ---: |
| Gold Chunk Recall@K | 0.75 | 0.85 |
| Top-1 Reference Hit | 0.30 | 0.45 |
| All Required Evidence@K | 0.65 | 0.80 |
| Stale Evidence Rate | 0.0625 | 0.075 |

第三组 50 条可回答案例：

| 指标 | Vector | Hybrid |
| --- | ---: | ---: |
| Hit@1 | 0.44 | 0.74 |
| Hit@3 | 0.74 | 0.98 |
| MRR | 0.60 | 0.85 |
| P50 | 152.66 ms | 115.38 ms |
| P95 | 168.26 ms | 184.99 ms |
| 平均上下文 Token | 103.48 | 101.82 |

Hybrid 的 Hit@1 提高 **30 个百分点**，但 P95 尾部延迟约增加 **9.9%**，旧证据率略高。这提醒我检索优化应一起看正确性、证据完整性、时效、延迟和成本，而不是只看 Recall。

今后面对文旅规划专业知识库中的标准编号、政策版本、项目名称与有效期，优先设计「语义检索 + 精确匹配 + 元数据/版本过滤」的可评测方案。**这是应用建议，尚未在真实文旅知识库上测出对应收益。**

### 3.3 D4：复用 Task08 的跨会话 PowerMem 实验

来源：[task08/README.md](../task08/README.md) 和 [d4_powermem_experience.py](../task08/d4_powermem_experience.py)。

我使用 PowerMem 1.1.7、SiliconFlow OpenAI-compatible LLM 和 seekDB Server 连接记忆系统，编写自己的 Memory Agent：

> 用户输入 → Memory Search → Prompt 注入 → LLM 回答 → Memory 提取 / 写入 → 下一轮召回。

在虚拟 Python/SaaS 开发者场景中进行了 **5 轮对话**。退出脚本并重新启动后，再询问之前提到的公司类型，能够正确回答「做 SaaS 产品的创业公司」。这验证了跨进程持久化和基础召回，**不能把实验中的虚拟人物设定误写成我个人真实职业背景**。

另一个更有价值的现象是 **Memory 污染**：

- 用户只表达 RabbitMQ 配置复杂；
- 助手建议尝试 Celery + Redis；
- 初版程序把用户输入与助手输出一起送入 Memory extraction；
- 助手建议被当作长期事实保存，之后又影响新的回答。

这说明「能够保存」与「应该保存」完全不同。后续需要区分 user-declared、assistant-generated、tool-observed、inferred、human-confirmed，并为记忆保留来源、时间、Scope、版本和纠错机制。

Task08 还验证了多用户隔离、Hot/Warm/Cold、先 dry-run 再清理、Handoff 历史快照和人工处理冲突等边界。

### 3.4 D5：我当前最需要补的能力

结合 Task06/Task08/Task09，我已经做过从工具到检索、从 Memory 到监控的多项实验，但还需要强化：

1. **可信数据与记忆治理：** 防止助手生成内容冒充用户事实，管理政策与项目版本，明确权威来源和访问范围。
2. **可复现的端到端测评：** 对固定任务同时记录任务成功、证据链、模型行为、故障阶段、Token 与真实成本。
3. **故障归因：** 遇到 400、404、Schema、检索缺失时，优先做最小化验证，不能一律归结为「模型不够强」。

---

## 4｜I8：PowerContext Harbor E2E 与 LoCoMo Plus

### 4.1 测评假设、数据与范围

**假设：** 在问题、模型和评分规则相同的条件下，加入准确提取并检索的历史 Memory，可能改善依赖长期历史线索的认知类回答；但完整 Memory 链路也会增加导入、提取、Embedding、召回等成本和失败点。

我选择两条互补的入口：

- **Harbor E2E：** 验证案例执行、Memory 采集/观测、原生验证和报告的工程链路。
- **LoCoMo Plus：** 尝试比较 query-only 与 memory 对实际答案质量的影响。

版本与数据来源：

| 项目 | 固定信息 |
| --- | --- |
| PowerContext | git commit **d0f669d5541bc7b391e840c7c6a951631b2a32ee** |
| LoCoMo Plus 来源 | xjtuleeyf/Locomo-Plus commit **059f4e3d38f7f1f96765e8e2cb7de3097551bffb** |
| 数据文件 | benchmark/locomo_plus/dataset/locomo_plus_smoke10.json |
| 数据范围 | 10 条有效认知类 smoke 样本；本次真实推理只选择前 2 条 |
| 样本类型 | 10 条中 causal 3、state 3、goal 2、value 2 |
| 诊断样本 ID | cognitive:0000、cognitive:0101 |
| 筛选规则 | 官方 smoke 固定顺序的前 2 条，未按答案表现重新挑选 |
| 历史 | 默认完整历史、不截断；Memory 组分别计划导入 20 和 26 个会话 |
| 已记录排除 | 数据检查报告记录 upstream 44 条格式异常排除案例，不是此次 2 条失分原因 |

这是固定子集诊断，不是 LoCoMo Plus 整体得分，也不能与论文或其它评测协议下的分数直接比较。

### 4.2 Harbor E2E：验收成功与离线复评

在 WSL2 Ubuntu 中检查 Docker/Compose/uv、锁定上述 PowerContext commit 并安装依赖后，执行：

~~~bash
cd ~/powercontext-i8
make harness-sync
uv sync --locked
make harness-compose-acceptance ARGS='--id locomo-support-group'
~~~

实际结果：

- Harbor 任务完成，**native task passed，reward=1.0**；
- 本次配置的 **11 项验收检查均通过**；
- 任务创建 1 条 Memory；
- probe_coverage=1；capture_coverage=0、groundedness=0 所对应的本次门槛均为 0，**不能因此宣称来源忠实度或记忆答案准确率达到 100%**；
- 生成 report.md、eval-report.json、replay.json 和 harbor-jobs/ 原生执行记录。

本地证据目录：

~~~text
~/powercontext-i8/.powercontext-e2e/bub/sqlite/acceptance/locomo-support-group/
~~~

再执行离线重新评分：

~~~bash
REPLAY=.powercontext-e2e/bub/sqlite/acceptance/locomo-support-group/replay.json POWERCONTEXT_E2E_OUTPUT=.powercontext-e2e/course/rescore make harness-rescore
~~~

离线重新评分成功，汇总指标与原验收一致。这一步复用冻结的 Replay，不重新调用模型，验证的是 **同一证据与评分条件下可重算**，不是新的独立问答质量实验。

### 4.3 LoCoMo Plus 数据检查与 Dry-run

运行：

~~~bash
cd ~/powercontext-i8
uv run python -m benchmark.locomo_plus inspect --dataset-file benchmark/locomo_plus/dataset/locomo_plus_smoke10.json
uv run python -m benchmark.locomo_plus run --dataset-file benchmark/locomo_plus/dataset/locomo_plus_smoke10.json --limit 10 --dry-run
~~~

确认 10 条样本可选择、历史会话完整、问题和评分任务可以生成。**Dry-run 不调用模型，不等于已完成真实基准测评。**

### 4.4 模型配置与兼容问题

实验环境：

- WSL2 Ubuntu + Docker Desktop；
- uv 项目依赖、PowerContext SQLite 隔离运行；
- 生成器 / Judge：SiliconFlow 上的 DeepSeek-V3；
- Embedding：BAAI/bge-m3，1024 维；
- 模型调用使用 OpenAI-compatible Chat Completions；
- 生成器与 Judge 使用**同一个模型**，因此评分不具备独立模型交叉验证的优势。

最初生成模型前缀为 **openai:deepseek-ai/DeepSeek-V3**，query-only 在 generation 阶段两题均报 ModelHTTPError / NotFoundError，没有有效评分。

我并没有立即认定模型下架，而是依次验证：

1. SiliconFlow 模型列表含 DeepSeek-V3 和 bge-m3；
2. 直接访问 /v1/chat/completions 返回 HTTP 200，简短输出 OK；
3. 将生成器和 Judge 模型前缀改为 **openai-chat:deepseek-ai/DeepSeek-V3**；
4. 重新运行 query-only 后，生成和评分成功。

**重要教训：** OpenAI-compatible 不代表 Responses 与 Chat Completions 两种调用协议可互换。模型 ID 和 Key 正确，也可能因为 SDK 默认协议不同而报错。

Memory 组仍出现独立故障：第一条历史会话提取阶段返回 PydanticAIConfigurationError → ModelHTTPError → BadRequestError。随后我用同一模型测试简单 JSON Mode，成功得到 `{"ok": true}`，但复杂结构化 Memory 提取的 HTTP 400 **仍未解决**；不能把简单 JSON 成功视为 Memory 提取成功。

### 4.5 两组实验的真实记录

**query-only 成功运行命令：**

~~~bash
uv run python -m benchmark.locomo_plus run --dataset-file benchmark/locomo_plus/dataset/locomo_plus_smoke10.json --env-file benchmark/locomo_plus/.env --judge-model "openai-chat:deepseek-ai/DeepSeek-V3" --limit 2 --arm query-only --run-id task09-query-only-chat-2
~~~

实际报告：

| 项目 | query-only |
| --- | ---: |
| 计划样本 | 2 |
| 完成生成并评分 | 2 |
| Judge 判正确 | 0 |
| Judge 判错误 | 2 |
| 质量分数 | 0.00% |
| generation / judge 失败 | 0 / 0 |
| 上下文 | 无历史；0 bytes |
| 生成用量 | 2 requests；输入 316 / 输出 55 tokens |
| Judge 用量 | 2 requests；输入 425 / 输出 90 tokens |
| 生成与 Judge 合计耗时 | 总执行约 9.45 秒 |
| USD 费用 | unknown（未配置价格表） |

两题分别是 cognitive:0000（causal）和 cognitive:0101（state），均被同模型 Judge 判为错误。没有历史证据的 query-only 是有效**无记忆基线**，但样本过少，不能推广为模型整体能力差。

**memory 运行命令：**

~~~bash
uv run python -m benchmark.locomo_plus run --dataset-file benchmark/locomo_plus/dataset/locomo_plus_smoke10.json --env-file benchmark/locomo_plus/.env --judge-model "openai-chat:deepseek-ai/DeepSeek-V3" --limit 2 --arm memory --run-id task09-memory-chat-2
~~~

实际报告：

| 项目 | memory |
| --- | ---: |
| 计划样本 | 2 |
| 完成评分 | **0** |
| 基础设施失败 | **2** |
| 历史会话计划数 | 样本 1：20；样本 2：26 |
| 成功处理的会话 | **0 / 20；0 / 26** |
| 失败位置 | 两条均在第 1 条历史会话 |
| 错误链 | PydanticAIConfigurationError → ModelHTTPError → BadRequestError |
| 历史导入累计耗时 | 约 34.28 秒 |
| Answer Quality | **unknown，不是 0%** |
| 费用 | unknown，失败请求可能也计费 |

**逐题状态：**

| Case ID | 类别 | query-only | memory |
| --- | --- | --- | --- |
| cognitive:0000 | causal | 已评分，wrong | 首个历史会话提取失败，未生成答案 |
| cognitive:0101 | state | 已评分，wrong | 首个历史会话提取失败，未生成答案 |

因此本次无法统计「仅 Memory 成功」「仅 query-only 成功」等有效配对差异，**更不能得出 Memory 导致效果下降或提升的结论**。实际已完成的是一个可复查的部分对照实验和一份故障定位记录。

### 4.6 成功与失败的证据路径

成功证据：

~~~text
~/powercontext-i8/.powercontext-e2e/bub/sqlite/acceptance/locomo-support-group/report.md
~/powercontext-i8/.powercontext-e2e/course/rescore/report.md
~/powercontext-i8/benchmark/locomo_plus/results/task09-query-only-chat-2/summary.md
~~~

失败证据：

~~~text
~/powercontext-i8/benchmark/locomo_plus/results/task09-memory-chat-2/summary.md
~/powercontext-i8/benchmark/locomo_plus/results/task09-memory-chat-2/ingestion.json
~/powercontext-i8/benchmark/locomo_plus/results/task09-memory-chat-2/observations.jsonl
~/powercontext-i8/benchmark/locomo_plus/results/task09-memory-chat-2/diagnostics/
~~~

这些是**本地证据路径，不是本 GitHub 仓库中的附件**。诊断目录可能包含原始对话、Prompt 和模型输出，本次不上传；API Key 保留在被忽略的 .env 中，绝不提交。

### 4.7 下一轮测评的修复方向

1. 从已保存的诊断记录核对完整结构化输出请求，定位是 JSON Schema、response_format、请求参数还是模型兼容性造成 HTTP 400；避免无依据更换模型或 Key。
2. 先用一条历史会话、一个固定模型验证 Memory extraction 与 Embedding，再考虑恢复完整历史，控制请求次数和成本。
3. 修复后使用**新的 run-id**，保留原失败记录，确保同一批题、相同历史选择与评分口径可配对。
4. 同时观察 Evidence retrieval、Answer quality、E2E success、延迟和 Token/真实费用。对失败场景分别归因为导入、提取、Embedding、召回、生成或评分。
5. 如果增加独立 Judge、人审或更多样本，要将新评测协议与本次结果分开标注。

---

## 5｜综合反思：从「会调用」走向「可靠交付」

### 5.1 最大收获

这次课程的主线在我看来变得更清晰：

> **数据和记忆决定 Agent 能拿到什么；模型决定如何理解；工具决定能执行什么；评测与监控决定能否证明任务真的完成。**

Task06 中 Hybrid 提升了 Hit@1，但部分查询仍然找错版本；Task08 中跨会话记忆有效，却出现助手建议污染 Memory；Task09 中 query-only 接口调通了，但 Memory 结构化提取未能完成。这些结果共同说明：单一模块成功不等于端到端可靠。

### 5.2 和 Personal AI OS / 文旅专业实践的联系

- **专业知识库：** 国家标准、政策和规划版本必须有准确来源、适用时间与引用；向量检索只负责发现候选，不应覆盖真实文件权威。
- **Personal AI OS：** 用户确认的长期事实、正式决策、临时建议、Agent 推断要有不同权限与生命周期，防止错误记忆在多个 Agent 间重复传播。
- **项目执行型 Agent：** 除了答案正确率，更要统计任务完成率、转人工、工具失败和安全降级；必要时明确交由人审。
- **投入决策：** 先得到真实需求量、成功率和成本，再谈 ROI；不要拿课程模拟收益替代实际投资判断。

### 5.3 当前薄弱环节和下一步

我目前更需要提升的不是继续堆叠框架，而是：

1. 建立最小、固定、可重复运行的个人 Agent 测试集；
2. 给关键知识与 Memory 增加 provenance、版本、Scope 与人工确认机制；
3. 学会读取失败证据，定位协议与 Schema 兼容，而不是只看终端最后一行报错；
4. 在真正的文旅知识库或业务 Agent 上逐步引入 P5 三层指标和运行监控。

不因为本次学习新增一套空泛项目；优先将这些能力用于既有知识库与 Agent 实践。

---

## 6｜文件、安全与复现说明

### 6.1 本地目录分工

- **本练习 GitHub 仓库：** 保存 Task01–Task09 的学习 README 和经过检查的练习代码。
- **官方课程克隆目录：** ~/easy-data-x-ai-course/code/P5，存放 P5 运行输出。
- **I8 独立研究目录：** ~/powercontext-i8，保留锁定 commit 的源代码、Harbor 输出和 LoCoMo Plus 诊断。

本次仅向 GitHub 提交这份经过整理的文字成果，不提交外部项目的 SQLite 数据库、完整测评对话或环境密钥。

### 6.2 复现前的注意事项

- 操作命令适用于 **WSL Ubuntu Bash**；Windows PowerShell 的路径与环境激活方法不同。
- P5 本地 Demo 不需商业模型 Key；I8 LoCoMo Plus 真正调用 SiliconFlow，可能产生费用。
- 在提交 GitHub 之前检查 git status 和 .gitignore，不要提交 .env、API Key、访问令牌及诊断目录。
- 实验环境及外部模型、依赖可能变化；本次对照以文中锁定的源代码版本及已记录结果为准。
- 成功的 11 项 Harbor E2E 检查并不等于模型回答准确率 100%；失败的 Memory 对照也不等于模型质量 0%。
- D5 的 D3/D4 数据来自此前 Task06/Task08 的实测记录，本次没有伪称重新运行这些实验。

## 7｜参考资料

- [Datawhale Easy Data × AI](https://github.com/datawhalechina/easy-data-x-ai)
- [P5 实践代码与运行说明](https://github.com/datawhalechina/easy-data-x-ai/tree/main/code/P5)
- [本仓库 Task06：Agentic RAG 对照与检索评测](../task06/README.md)
- [本仓库 Task08：PowerMem 与 PowerContext 实践](../task08/README.md)
- [PowerContext 固定版本](https://github.com/oceanbase/powercontext/tree/d0f669d5541bc7b391e840c7c6a951631b2a32ee)
- [PowerContext Harbor E2E 指南](https://github.com/oceanbase/powercontext/blob/d0f669d5541bc7b391e840c7c6a951631b2a32ee/e2e/bub/README.md)
- [PowerContext LoCoMo Plus 指南](https://github.com/oceanbase/powercontext/blob/d0f669d5541bc7b391e840c7c6a951631b2a32ee/benchmark/locomo_plus/README.md)

---

**Task09 结语：** 这次不仅完成了 P5 的离线评测、ROI、测试和监控，也在 I8 中经历了真实的测评协议适配和 Memory 故障定位。我开始从「实验跑通」转向「结果有证据、失败能归因、成本可解释、业务可度量」的 Agent 工程思维。后续重点不是掩盖尚未完成的 Memory 对照，而是保留问题并用可复现的更小实验解决它。
