# Codex Grok 视频流水线

[English](README.md)

把 Codex 和你本人持有的 SuperGrok 订阅连接成一条本地端到端 AI 视频工作流：

```text
剧本 → 首帧 → 视频提示词 → Grok Imagine → 本地 MP4 → 质检 → 剪辑
```

以前，Codex 写完剧本、首帧和提示词后，人还要打开 Grok 网页、上传图片、复制提示词、等待生成、下载视频，再把文件交回 Codex。这个插件把中间的“人肉 API”变成 Codex 可重复调用的本地 Skill。

> [!IMPORTANT]
> 这是非官方社区互操作项目，与 OpenAI、xAI、Grok、Nous Research、Hermes Agent 或 progrok 均无隶属或背书关系。本项目不绕过配额或产品限制。只能使用自己合法持有并获准自动化操作的账号；真实生成会消耗订阅次数或额度。

## 两种后端

| 后端 | 适用场景 | 安装方式 |
| --- | --- | --- |
| `progrok` | 安装最短，直接提供视频 CLI | `npm install -g progrok && progrok login` |
| `hermes` | 已实测的 Hermes OAuth 与 Codex Responses 兼容路线 | 参见 [Hermes 高级配置](docs/hermes-advanced.md) |

`auto` 模式会优先使用已经安装的 `progrok`；否则检查 `http://127.0.0.1:8645/v1` 上的 Hermes 本机代理。

## 五分钟开始

### 1. 安装并登录本地 OAuth 桥

推荐的简便路线：

```bash
npm install -g progrok
progrok login
progrok status
```

OAuth 凭据由桥接工具保存在本机。本插件不会读取或打印凭据文件。

### 2. 安装 Codex Skill

```bash
git clone https://github.com/13111655587xl-jpg/codex-grok-video-pipeline.git
mkdir -p "$HOME/.agents/skills"
cp -R codex-grok-video-pipeline/skills/grok-imagine-video "$HOME/.agents/skills/"
```

重启 Codex，让它重新发现 Skill。仓库同时包含已经验证的 `.codex-plugin/plugin.json`，便于本地插件开发以及后续进入 Marketplace。

### 3. 直接告诉 Codex

```text
用 Grok Imagine 生成一个 5 秒、16:9 的视频：
红色纸飞机在干净的蓝色影棚中滑翔。
保存到 ./output，下载后检查视频是否有效。
```

或者直接运行：

```bash
python3 skills/grok-imagine-video/scripts/grok_video.py generate \
  --prompt "红色纸飞机在干净的蓝色影棚中滑翔" \
  --duration 5 --aspect-ratio 16:9 --resolution 480p \
  --output "$PWD/output/paper-airplane.mp4"
```

图生视频：

```bash
python3 skills/grok-imagine-video/scripts/grok_video.py generate \
  --image "$PWD/first-frame.png" \
  --prompt "自然细微动作，镜头缓慢推进" \
  --duration 5 --aspect-ratio 16:9 --resolution 720p \
  --output "$PWD/output/shot-01.mp4"
```

只检查参数、不提交生成：

```bash
python3 skills/grok-imagine-video/scripts/grok_video.py generate \
  --prompt "test" --output "$PWD/output/test.mp4" --dry-run
```

## 它解决的不只是一次 API 调用

- Codex 自动决定文生视频还是图生视频。
- 自动提交、轮询、下载并保存本地 MP4。
- Hermes 后端立即写入元数据，任务中断后可以恢复。
- 下载完成后检查文件大小，并在可用时调用 `ffprobe`。
- 只有本地成片真正存在后才向用户交付。
- 下一步可以直接衔接剪辑 Skill，不再人工搬运素材。

## 安全边界

- OAuth 代理只绑定 `127.0.0.1`，不要暴露到公网。
- 不提交 auth 文件、refresh token、带凭据的日志和私人生成素材。
- 不共享账号、不出售订阅访问、不运行账号池。
- 上游协议可能随时变化，正式使用时应锁定版本。

更多信息见 [SECURITY.md](SECURITY.md) 和 [DISCLAIMER.md](DISCLAIMER.md)。

## 为什么这个项目存在

OAuth 代理本身已有多个社区实现。本项目的定位不是再造账号代理，而是补齐 Codex 原生视频生产层：从创作任务到经过验证的本地媒体，再无缝进入剪辑。

## 文档

- [架构](docs/architecture.md)
- [Hermes 高级配置](docs/hermes-advanced.md)
- [开源文章](docs/article.zh-CN.md)

## 许可证

MIT。第三方项目、服务、订阅和商标仍受各自许可证与条款约束。
