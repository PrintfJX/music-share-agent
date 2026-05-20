from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage

# =========================
# 配置 DeepSeek API Key
# =========================

apiKey = "sk-xxx" # 设置你的 DeepSeek API Key

# =========================
# 创建 DeepSeek 模型
# =========================

llm = ChatDeepSeek(
    api_key=apiKey,
    model="deepseek-v4-flash",
    temperature=0.7,
    max_tokens=1024,
    timeout=60,
    max_retries=3
)

# =========================
# 构造聊天消息
# =========================

messages = [
    SystemMessage(
        content="你是一名专业 Python 教师。"
    ),

    HumanMessage(
        content="请解释什么是 LangChain，并给出简单示例。"
    )
]

# =========================
# 调用模型
# =========================

response = llm.invoke(messages)

# =========================
# 输出结果
# =========================

print("AI 回复：")
print(response.content)