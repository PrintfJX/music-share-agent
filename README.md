# 网易云音乐 Agent

基于 LangChain 的网易云音乐风格查询 Agent，通过 NapCatQQ 直接分享链接到 QQ。

## 功能

- 🎵 根据音乐风格搜索歌曲（流行、摇滚、民谣、电子等）
- 🔍 根据关键词搜索歌曲/歌手
- 📋 查找特定标签的歌单
- 📤 通过 NapCatQQ 直接分享到 QQ 好友/群
- 👥 查看好友/群列表

## 安装

```bash
pip install -r requirements.txt
```

## 配置

### 1. 创建 `.env` 文件

```env
# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key

# NapCat 配置
NAPCAT_HTTP_URL=http://127.0.0.1:3000
NAPCAT_WS_URL=ws://127.0.0.1:3001
NAPCAT_ACCESS_TOKEN=your_access_token
```

### 2. 安装并运行 NapCatQQ

NapCatQQ 是基于 QQNT 的 OneBot 11 实现，可以直接登录你的 QQ 号。

**安装方式：**

1. 下载 [NapCatQQ](https://github.com/NapNapX/NapCatQQ)
2. 安装 QQNT 版本的 QQ 客户端
3. 运行 NapCat，扫码登录你的 QQ 号
4. NapCat 会提供 HTTP API（默认端口 3000）和 WebSocket（默认端口 3001）

**详细配置请参考：** https://napneap.github.io/napcat/

## 使用

### 交互模式
```bash
python music_agent.py
```

### 测试模式
```bash
python music_agent.py --test
```

## 示例对话

```
📝 你: 帮我找一些摇滚风格的歌曲
🤖 助手: 🎵 找到 10 首 '摇滚' 风格的歌曲：
1. 《海阔天空》 - Beyond
   专辑：乐与怒
   链接：https://music.163.com/song?id=xxx
...

📝 你: 把第一首分享给我的好友 123456789
🤖 助手: ✅ 消息发送成功！

📝 你: 查看我的群列表
🤖 助手: 📋 共 5 个群：
...
```

## 可用工具

| 工具 | 功能 |
|------|------|
| `search_music_by_style` | 根据风格搜索歌曲 |
| `search_music_by_keyword` | 根据关键词搜索 |
| `get_song_detail` | 获取歌曲详情 |
| `get_playlist_by_tag` | 获取歌单 |
| `share_to_qq_friend` | 分享到 QQ 好友 |
| `share_to_qq_group` | 分享到 QQ 群 |
| `format_music_share` | 格式化分享消息 |
| `check_napcat_connection` | 检查 NapCat 连接 |
| `get_qq_friends` | 获取好友列表 |
| `get_qq_groups` | 获取群列表 |

## 网易云音乐 API

使用公开 API 服务，你也可以部署自己的：
- [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)

修改 `music_tools.py` 中的 `NETEASE_API_BASE` 即可。
