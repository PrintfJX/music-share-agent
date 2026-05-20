"""网易云音乐 Agent - 基于风格查询并分享到 QQ (NapCat)"""
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import sys

# 设置输出编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from music_tools import (
    search_music_by_style,
    search_music_by_keyword,
    get_song_detail,
    get_playlist_by_tag,
    share_to_qq_friend,
    share_to_qq_group,
    share_music_with_image_to_friend,
    share_music_with_image_to_group,
    format_music_share,
    format_music_share_with_image,
    get_anime_image,
    check_napcat_connection,
    get_qq_friends,
    get_qq_groups
)

load_dotenv()


def create_music_agent():
    """创建网易云音乐查询 Agent"""

    # 初始化 LLM
    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0.7,
    )

    # 定义工具列表
    tools = [
        search_music_by_style,
        search_music_by_keyword,
        get_song_detail,
        get_playlist_by_tag,
        share_to_qq_friend,
        share_to_qq_group,
        share_music_with_image_to_friend,
        share_music_with_image_to_group,
        format_music_share,
        format_music_share_with_image,
        get_anime_image,
        check_napcat_connection,
        get_qq_friends,
        get_qq_groups
    ]

    # 使用 langchain.agents 创建 Agent
    system_prompt = """你是一个专业的网易云音乐助手，帮助用户查找和分享音乐到 QQ。

工具使用指南：
1. 搜索音乐风格（流行、摇滚、民谣等）→ search_music_by_style
2. 搜索歌曲/歌手 → search_music_by_keyword
3. 获取歌曲详情 → get_song_detail
4. 查找歌单 → get_playlist_by_tag
5. 分享带图片的歌曲到好友 → share_music_with_image_to_friend（推荐，自动配二次元图片）
6. 分享带图片的歌曲到群 → share_music_with_image_to_group（推荐，自动配二次元图片）
7. 分享纯文本到好友 → share_to_qq_friend
8. 分享纯文本到群 → share_to_qq_group
9. 获取随机二次元图片 → get_anime_image
10. 检查 NapCat 连接 → check_napcat_connection
11. 获取好友列表 → get_qq_friends
12. 获取群列表 → get_qq_groups

分享流程（推荐）：
- 用户想分享歌曲时，直接使用 share_music_with_image_to_friend 或 share_music_with_image_to_group
- 这两个工具会自动获取二次元图片并发送图文消息
- 需要提供：QQ号/群号、歌曲名、歌手、歌曲链接

重要提示：
- 返回歌曲信息时，始终包含网易云音乐链接
- 分享音乐时优先使用带图片的分享工具
- 用中文回复用户
- 如果 NapCat 连接失败，提示用户检查 NapCat 是否运行"""

    agent = create_agent(llm, tools, system_prompt=system_prompt)

    return agent


def run_interactive():
    """交互式运行 Agent"""
    agent = create_music_agent()

    print("=" * 60)
    print("网易云音乐助手已启动！(NapCatQQ)")
    print("=" * 60)
    print("你可以：")
    print("  - 搜索特定风格的音乐（如：找一些摇滚风格的歌曲）")
    print("  - 搜索歌曲或歌手（如：搜索周杰伦的歌）")
    print("  - 查找歌单（如：找一些华语歌单）")
    print("  - 分享歌曲到 QQ 好友或群")
    print("  - 查看好友/群列表")
    print("  - 检查 NapCat 连接状态")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 60)

    # 检查 NapCat 连接
    print("\n正在检查 NapCat 连接...")
    try:
        result = check_napcat_connection.invoke({})
        print(result)
    except Exception as e:
        print(f"NapCat 连接检查失败: {str(e)}")
        print("请确保 NapCat 正在运行，并配置正确的 NAPCAT_HTTP_URL")

    while True:
        try:
            user_input = input("\n你: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break

            if not user_input:
                continue

            # 调用 Agent
            response = agent.invoke({"messages": [{"role": "user", "content": user_input}]})

            # 获取最后一条 AI 消息
            last_message = response["messages"][-1]
            print(f"\n助手: {last_message.content}")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")


def run_test():
    """测试 Agent 功能"""
    agent = create_music_agent()

    test_questions = [
        "帮我找一些流行风格的歌曲",
        "搜索周杰伦的歌",
        "检查 NapCat 连接状态",
    ]

    print("=" * 60)
    print("测试模式")
    print("=" * 60)

    for question in test_questions:
        print(f"\n测试问题: {question}")
        print("-" * 60)

        try:
            response = agent.invoke({"messages": [{"role": "user", "content": question}]})
            last_message = response["messages"][-1]
            print(f"回答: {last_message.content}")
        except Exception as e:
            print(f"错误: {str(e)}")

        print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test()
    else:
        run_interactive()