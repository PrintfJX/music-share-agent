from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from dotenv import load_dotenv

from tools import calculator,  get_weather
load_dotenv()

llm=ChatDeepSeek(
    model="deepseek-v4-flash",
    temperature=0.7,
    model_kwargs={"reasoning_effort": None},
)

agent = create_agent(
    model=llm,
    tools=[calculator, get_weather],  
    system_prompt="""你是一个有用的AI助手。
    
你可以使用以下工具来帮助用户：
- calculator：执行数学计算
- get_weather：查询天气信息

当用户提问时，判断是否需要使用工具来获得更准确的答案。
如果需要，就调用相应的工具。最后用中文回答用户的问题。"""
)

if __name__ == "__main__":
    
    test_questions = [
        "帮我计算 123 * 456 等于多少?",
        "北京的天气如何？",
        "帮我计算 (100 + 50) * 2，然后告诉我结果"
    ]
    
    for question in test_questions:
        print(f"\n📝 用户: {question}")
        print("-" * 60)
        
        response = agent.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )
        
        # 获取最后一条消息（Agent的最终回答）
        final_message = response["messages"][-1]
        print(f"🤖 助手: {final_message.content}")