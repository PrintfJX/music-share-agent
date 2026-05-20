"""网易云音乐相关工具 + NapCatQQ WebSocket 发送"""
from langchain.tools import tool
import requests
import json
import os
import asyncio
import websockets
from typing import Optional
from dotenv import load_dotenv

# 先加载环境变量
load_dotenv()

# 网易云音乐 API 基础地址（多个备用）
NETEASE_API_LIST = [
    "https://netease-cloud-music-api-mk7r.vercel.app",
    "https://netease-cloud-music-api-lk7k.vercel.app",
    "https://netease-cloud-music-api-five-roan-88.vercel.app",
]
NETEASE_API_BASE = NETEASE_API_LIST[0]  # 默认使用第一个


def try_netease_api(endpoint: str, params: dict, timeout: int = 8) -> dict:
    """尝试多个网易云音乐 API 直到成功

    Args:
        endpoint: API 端点（如 /cloudsearch）
        params: 请求参数
        timeout: 超时时间

    Returns:
        API 响应数据
    """
    for api_base in NETEASE_API_LIST:
        try:
            url = f"{api_base}{endpoint}"
            response = requests.get(url, params=params, timeout=timeout)
            data = response.json()
            if data.get("code") == 200:
                return data
        except Exception:
            continue
    return {"code": -1, "error": "所有 API 均不可用"}

# 南风 API 二次元图片（备用多个 API）
ANIME_API_LIST = [
    "https://api.lolicon.app/setu/v2",
    "https://www.loliapi.com/acg/pc/",
    "https://api.yimian.xyz/img?type=moe&size=1920x1080",
]

# NapCat WebSocket 配置
NAPCAT_WS_URL = os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:3001")
NAPCAT_ACCESS_TOKEN = os.getenv("NAPCAT_ACCESS_TOKEN", "")


async def ws_call(action: str, params: dict) -> dict:
    """通过 WebSocket 调用 NapCat API"""
    ws_url = f"{NAPCAT_WS_URL}?access_token={NAPCAT_ACCESS_TOKEN}" if NAPCAT_ACCESS_TOKEN else NAPCAT_WS_URL

    try:
        async with websockets.connect(ws_url) as ws:
            # 等待连接建立事件
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)

            # 收到 lifecycle 事件后发送 API 请求
            request = {
                "action": action,
                "params": params,
                "echo": "music_agent"
            }
            await ws.send(json.dumps(request))

            # 接收 API 响应
            while True:
                response = await asyncio.wait_for(ws.recv(), timeout=10)
                data = json.loads(response)
                # 返回带有 echo 或 retcode 的响应
                if data.get("echo") == "music_agent" or data.get("retcode") is not None:
                    return data
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def sync_ws_call(action: str, params: dict) -> dict:
    """同步包装 WebSocket 调用"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(ws_call(action, params))
        loop.close()
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def send_napcat_message(target_id: int, message: str, is_group: bool = False) -> str:
    """通过 NapCat WebSocket 发送消息

    Args:
        target_id: 目标ID（QQ号或群号）
        message: 消息内容（可以是文本或消息链）
        is_group: 是否群消息

    Returns:
        发送结果
    """
    if is_group:
        action = "send_group_msg"
        params = {"group_id": target_id, "message": message}
    else:
        action = "send_private_msg"
        params = {"user_id": target_id, "message": message}

    result = sync_ws_call(action, params)

    if result.get("status") == "ok" or result.get("retcode") == 0:
        msg_id = result.get("data", {}).get("message_id", "")
        return f"消息发送成功！ID: {msg_id}"
    elif "error" in result:
        return f"连接失败: {result['error']}\n请确保 NapCat WebSocket 正在运行于 {NAPCAT_WS_URL}"
    else:
        return f"发送失败: {result.get('wording', result.get('message', '未知错误'))}"


def send_napcat_image(target_id: int, image_url: str, is_group: bool = False) -> str:
    """通过 NapCat WebSocket 发送图片消息

    Args:
        target_id: 目标ID（QQ号或群号）
        image_url: 图片链接
        is_group: 是否群消息

    Returns:
        发送结果
    """
    # NapCat 消息链格式发送图片
    message_chain = [
        {"type": "image", "data": {"url": image_url}}
    ]

    if is_group:
        action = "send_group_msg"
        params = {"group_id": target_id, "message": message_chain}
    else:
        action = "send_private_msg"
        params = {"user_id": target_id, "message": message_chain}

    result = sync_ws_call(action, params)

    if result.get("status") == "ok" or result.get("retcode") == 0:
        msg_id = result.get("data", {}).get("message_id", "")
        return f"图片发送成功！ID: {msg_id}"
    elif "error" in result:
        return f"连接失败: {result['error']}"
    else:
        return f"发送失败: {result.get('wording', result.get('message', '未知错误'))}"


def send_napcat_message_with_image(target_id: int, text: str, image_url: str, is_group: bool = False) -> str:
    """通过 NapCat WebSocket 发送图文消息

    Args:
        target_id: 目标ID（QQ号或群号）
        text: 文本内容
        image_url: 图片链接
        is_group: 是否群消息

    Returns:
        发送结果
    """
    # NapCat 消息链格式：先图片后文字
    message_chain = [
        {"type": "image", "data": {"url": image_url}},
        {"type": "text", "data": {"text": text}}
    ]

    if is_group:
        action = "send_group_msg"
        params = {"group_id": target_id, "message": message_chain}
    else:
        action = "send_private_msg"
        params = {"user_id": target_id, "message": message_chain}

    result = sync_ws_call(action, params)

    if result.get("status") == "ok" or result.get("retcode") == 0:
        msg_id = result.get("data", {}).get("message_id", "")
        return f"图文消息发送成功！ID: {msg_id}"
    elif "error" in result:
        return f"连接失败: {result['error']}"
    else:
        return f"发送失败: {result.get('wording', result.get('message', '未知错误'))}"


# ==================== 网易云音乐工具 ====================

@tool
def search_music_by_style(style: str, limit: int = 10) -> str:
    """根据音乐风格搜索网易云音乐歌曲。

    支持的风格：流行、摇滚、民谣、电子、说唱、古典、爵士、R&B、金属等。

    Args:
        style: 音乐风格
        limit: 返回数量，默认10

    Returns:
        歌曲列表（含歌名、歌手、链接）
    """
    data = try_netease_api("/cloudsearch", {"keywords": style, "limit": limit, "type": 1})

    if data.get("code") != 200 or not data.get("result", {}).get("songs"):
        return f"未找到风格为 '{style}' 的歌曲，或 API 暂时不可用"

    songs = data["result"]["songs"][:limit]
    output = f"找到 {len(songs)} 首 '{style}' 风格的歌曲：\n\n"

    for i, song in enumerate(songs, 1):
        name = song.get("name", "未知")
        artist = ", ".join([ar.get("name", "") for ar in song.get("ar", [])])
        album = song.get("al", {}).get("name", "未知")
        song_id = song.get("id")
        link = f"https://music.163.com/song?id={song_id}"
        output += f"{i}. 《{name}》 - {artist}\n"
        output += f"   专辑：{album}\n"
        output += f"   ID：{song_id}\n"
        output += f"   链接：{link}\n\n"

    return output


@tool
def search_music_by_keyword(keyword: str, limit: int = 10) -> str:
    """根据关键词搜索歌曲。

    Args:
        keyword: 搜索关键词（歌名/歌手/专辑）
        limit: 返回数量

    Returns:
        歌曲列表
    """
    data = try_netease_api("/cloudsearch", {"keywords": keyword, "limit": limit, "type": 1})

    if data.get("code") != 200 or not data.get("result", {}).get("songs"):
        return f"未找到与 '{keyword}' 相关的歌曲，或 API 暂时不可用"

    songs = data["result"]["songs"][:limit]
    output = f"搜索 '{keyword}' 找到 {len(songs)} 首歌曲：\n\n"

    for i, song in enumerate(songs, 1):
        name = song.get("name", "未知")
        artist = ", ".join([ar.get("name", "") for ar in song.get("ar", [])])
        song_id = song.get("id")
        link = f"https://music.163.com/song?id={song_id}"
        output += f"{i}. 《{name}》 - {artist}\n"
        output += f"   ID：{song_id}\n"
        output += f"   链接：{link}\n\n"

    return output


@tool
def get_song_detail(song_id: int) -> str:
    """获取歌曲详情。

    Args:
        song_id: 歌曲ID

    Returns:
        歌曲详细信息
    """
    try:
        url = f"{NETEASE_API_BASE}/song/detail"
        response = requests.get(url, params={"ids": song_id}, timeout=10)
        data = response.json()

        if data.get("code") != 200 or not data.get("songs"):
            return f"未找到歌曲ID: {song_id}"

        song = data["songs"][0]
        duration_ms = song.get("dt", 0)
        minutes = duration_ms // 1000 // 60
        seconds = duration_ms // 1000 % 60

        output = f"歌曲详情\n"
        output += f"━━━━━━━━━━━━━━━━━━\n"
        output += f"歌名：{song.get('name')}\n"
        output += f"歌手：{', '.join([ar['name'] for ar in song.get('ar', [])])}\n"
        output += f"专辑：{song.get('al', {}).get('name')}\n"
        output += f"时长：{minutes}分{seconds}秒\n"
        output += f"ID：{song.get('id')}\n"
        output += f"链接：https://music.163.com/song?id={song.get('id')}"

        return output

    except Exception as e:
        return f"获取详情出错：{str(e)}"


@tool
def get_playlist_by_tag(tag: str, limit: int = 10) -> str:
    """根据标签获取歌单。

    Args:
        tag: 歌单标签（华语、流行、摇滚、民谣、电子、ACG等）
        limit: 返回数量

    Returns:
        歌单列表
    """
    try:
        url = f"{NETEASE_API_BASE}/top/playlist"
        params = {"cat": tag, "limit": limit}

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("code") != 200 or not data.get("playlists"):
            return f"未找到标签为 '{tag}' 的歌单"

        playlists = data["playlists"]
        output = f"找到 {len(playlists)} 个 '{tag}' 歌单：\n\n"

        for i, pl in enumerate(playlists, 1):
            play_count = pl.get("playCount", 0)
            if play_count >= 10000:
                play_count_str = f"{play_count // 10000}万"
            else:
                play_count_str = str(play_count)

            output += f"{i}. 《{pl.get('name')}》\n"
            output += f"   创建者：{pl.get('creator', {}).get('nickname', '未知')}\n"
            output += f"   播放量：{play_count_str}\n"
            output += f"   链接：https://music.163.com/playlist?id={pl.get('id')}\n\n"

        return output

    except Exception as e:
        return f"获取歌单出错：{str(e)}"


# ==================== NapCatQQ WebSocket 工具 ====================

@tool
def share_to_qq_friend(user_id: int, content: str) -> str:
    """分享内容到 QQ 好友（私聊）。

    通过 NapCat WebSocket 发送私聊消息。
    需配置环境变量：NAPCAT_WS_URL, NAPCAT_ACCESS_TOKEN

    Args:
        user_id: QQ 号
        content: 发送内容

    Returns:
        发送结果
    """
    return send_napcat_message(user_id, content, is_group=False)


@tool
def share_to_qq_group(group_id: int, content: str) -> str:
    """分享内容到 QQ 群。

    通过 NapCat WebSocket 发送群消息。

    Args:
        group_id: 群号
        content: 发送内容

    Returns:
        发送结果
    """
    return send_napcat_message(group_id, content, is_group=True)


@tool
def share_music_with_image_to_friend(user_id: int, song_name: str, artist: str, link: str) -> str:
    """分享带二次元图片的歌曲到 QQ 好友。

    自动获取二次元图片并发送图文消息。

    Args:
        user_id: QQ 号
        song_name: 歌曲名
        artist: 歌手
        link: 歌曲链接

    Returns:
        发送结果
    """
    # 获取二次元图片
    image_url = get_anime_image.invoke({})

    # 格式化文本
    text = f"""分享一首好歌

《{song_name}》- {artist}

点击收听：{link}

— 来自网易云音乐助手"""

    return send_napcat_message_with_image(user_id, text, image_url, is_group=False)


@tool
def share_music_with_image_to_group(group_id: int, song_name: str, artist: str, link: str) -> str:
    """分享带二次元图片的歌曲到 QQ 群。

    自动获取二次元图片并发送图文消息。

    Args:
        group_id: 群号
        song_name: 歌曲名
        artist: 歌手
        link: 歌曲链接

    Returns:
        发送结果
    """
    # 获取二次元图片
    image_url = get_anime_image.invoke({})

    # 格式化文本
    text = f"""分享一首好歌

《{song_name}》- {artist}

点击收听：{link}

— 来自网易云音乐助手"""

    return send_napcat_message_with_image(group_id, text, image_url, is_group=True)


@tool
def format_music_share(song_name: str, artist: str, link: str) -> str:
    """格式化音乐分享消息。

    Args:
        song_name: 歌曲名
        artist: 歌手
        link: 歌曲链接

    Returns:
        格式化的分享消息
    """
    return f"""分享一首好歌

《{song_name}》- {artist}

点击收听：{link}

— 来自网易云音乐助手"""


@tool
def get_anime_image() -> str:
    """获取一张随机二次元图片链接。

    Returns:
        二次元图片链接
    """
    # 尝试多个 API
    apis = [
        ("LoliAPI", "https://www.loliapi.com/acg/pc/"),
        ("亦面API", "https://api.yimian.xyz/img?type=moe&size=1920x1080"),
        ("Pixiv", "https://api.lolicon.app/setu/v2"),
    ]

    for name, url in apis:
        try:
            if "lolicon" in url:
                # Lolicon API 需要 POST
                response = requests.post(url, json={"r18": 0, "size": ["regular"]}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data"):
                        return data["data"][0].get("urls", {}).get("regular", "")
            else:
                response = requests.get(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    # 如果最终 URL 是图片
                    final_url = response.url
                    if final_url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) or 'img' in final_url or 'acg' in final_url:
                        return final_url
        except Exception:
            continue

    # 所有 API 都失败，返回一个可用的备用地址
    return "https://www.loliapi.com/acg/pc/"


@tool
def format_music_share_with_image(song_name: str, artist: str, link: str) -> str:
    """格式化带二次元图片的音乐分享消息。

    Args:
        song_name: 歌曲名
        artist: 歌手
        link: 歌曲链接

    Returns:
        格式化的分享消息（含二次元图片链接）
    """
    image_url = get_anime_image.invoke({})
    return f"""分享一首好歌

《{song_name}》- {artist}

点击收听：{link}

二次元图片：{image_url}

— 来自网易云音乐助手"""


@tool
def check_napcat_connection() -> str:
    """检查 NapCat WebSocket 连接状态。

    Returns:
        连接状态和登录信息
    """
    result = sync_ws_call("get_login_info", {})

    if result.get("status") == "ok" or result.get("retcode") == 0:
        user_info = result.get("data", {})
        qq = user_info.get("user_id", "未知")
        nickname = user_info.get("nickname", "未知")
        return f"NapCat WebSocket 连接正常\n已登录 QQ: {qq} ({nickname})"
    elif "error" in result:
        return f"无法连接 NapCat WebSocket\n错误: {result['error']}\n请确保 NapCat 正在运行于: {NAPCAT_WS_URL}"
    else:
        return f"NapCat 响应异常: {result.get('wording', result.get('message', '未知'))}"


@tool
def get_qq_friends() -> str:
    """获取 QQ 好友列表。

    Returns:
        好友列表
    """
    result = sync_ws_call("get_friend_list", {})

    if result.get("status") == "ok" or result.get("retcode") == 0:
        friends = result.get("data", [])
        output = f"共 {len(friends)} 位好友：\n\n"
        for f in friends[:20]:
            output += f"• {f.get('nickname', '未知')} ({f.get('user_id', '')})\n"
        if len(friends) > 20:
            output += f"\n... 还有 {len(friends) - 20} 位好友"
        return output
    elif "error" in result:
        return f"连接失败: {result['error']}"
    else:
        return f"获取失败: {result.get('wording', result.get('message', '未知'))}"


@tool
def get_qq_groups() -> str:
    """获取 QQ 群列表。

    Returns:
        群列表
    """
    result = sync_ws_call("get_group_list", {})

    if result.get("status") == "ok" or result.get("retcode") == 0:
        groups = result.get("data", [])
        output = f"共 {len(groups)} 个群：\n\n"
        for g in groups:
            output += f"• {g.get('group_name', '未知')} ({g.get('group_id', '')})\n"
        return output
    elif "error" in result:
        return f"连接失败: {result['error']}"
    else:
        return f"获取失败: {result.get('wording', result.get('message', '未知'))}"