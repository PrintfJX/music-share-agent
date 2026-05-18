from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

load_dotenv()

llm=ChatDeepSeek(
    model="deepseek-v4-flash",
    temperature=0.7,
)

agent=create_agent(
    model=llm,
    tools=[],
    system_prompt="你是一个友好、有帮助的AI助手。用中文回答用户的问题。"
)

# 现在让我们测试这个 Agent
if __name__ == "__main__":
    # 向 Agent 提问
    user_question = "你好！请介绍一下你自己。"
    
    print(f"用户: {user_question}")
    print("-" * 50)
    
    # 调用 Agent（invoke 表示"调用"）
    response = agent.invoke(
        {
            "messages": [{"role": "user", "content": user_question}]
        }
    )
    
    # 获取 Agent 的最终回答
    final_message = response["messages"][-1]
    print(f"助手: {final_message.content}")
