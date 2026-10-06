from openai import OpenAI
from powermem import Memory, auto_config


USER_ID = "task08_memory_agent_user"


# 1. 加载 PowerMem 配置
config = auto_config()
llm_config = config["llm"]["config"]

# 2. 初始化 SiliconFlow / OpenAI-compatible Client
client = OpenAI(
    api_key=llm_config["api_key"],
    base_url=llm_config["openai_base_url"],
)

model = llm_config["model"]

# 3. 初始化长期记忆
memory = Memory(config=config)


def search_memories(query: str):
    """检索与当前问题相关的长期记忆。"""
    result = memory.search(
        query=query,
        user_id=USER_ID,
        limit=5,
    )

    return [
        item["memory"]
        for item in result.get("results", [])
        if item.get("memory")
    ]


def chat(user_input: str):
    """检索记忆 → 注入上下文 → LLM 回答 → 写入新记忆。"""

    # Step 1：想起相关记忆
    memories = search_memories(user_input)

    if memories:
        memory_context = "\n".join(
            f"- {item}" for item in memories
        )
    else:
        memory_context = "暂无相关长期记忆。"

    # Step 2：将记忆注入 Agent 上下文
    system_prompt = f"""
你是一个带长期记忆能力的 AI 助手。

以下是从长期记忆系统中检索到的用户信息：

{memory_context}

回答时：
1. 在相关时自然使用这些记忆；
2. 不要生硬复述全部记忆；
3. 不要编造记忆中不存在的信息；
4. 用户的表达偏好如果已经记录，应尽量遵守。
""".strip()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    # Step 3：将本轮对话交给 PowerMem 提炼并保存
    memory.add(
        messages=[
            {
                "role": "user",
                "content": user_input,
            },
            {
                "role": "assistant",
                "content": answer,
            },
        ],
        user_id=USER_ID,
    )

    print("\n[本轮召回的记忆]")
    if memories:
        for item in memories:
            print("-", item)
    else:
        print("- 无")

    print("\n[Agent]")
    print(answer)


print("=" * 60)
print("D4 PowerMem Memory Agent")
print("输入 quit 退出。")
print("=" * 60)

while True:
    user_input = input("\n你：").strip()

    if user_input.lower() in {"quit", "exit"}:
        print("已退出。")
        break

    if not user_input:
        continue

    try:
        chat(user_input)
    except Exception as exc:
        print("\n[ERROR]")
        print(type(exc).__name__, exc)