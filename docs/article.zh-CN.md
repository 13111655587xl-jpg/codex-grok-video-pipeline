# 我让 Codex 和 SuperGrok 不再靠我“人肉传文件”

我同时订阅了 Codex Plus 和 SuperGrok。

以前制作 AI 视频时，Codex 可以写剧本、拆分镜、生成首帧，还能把 Grok Imagine 的提示词写得很细。但到了真正生成视频这一步，工作流突然断了：我需要打开 Grok 网页，复制提示词，上传首帧，等待生成，下载 MP4，再把文件交回 Codex 剪辑。

两个很聪明的 AI，中间靠我做人肉 API。

## 我真正想解决的问题

我没有开 xAI API，因为已经在支付 SuperGrok 订阅。我也不是要绕过配额，而是希望自己合法持有的两份订阅能组成一条完整工作流：

```text
Codex 写剧本
  → 设计分镜和首帧
  → 写视频提示词
  → 调用 Grok Imagine
  → 自动等待并下载 MP4
  → 检查视频是否有效
  → 直接进入 Codex 剪辑
```

## 技术路线

社区里已经有一些工具，可以把本人账号的 xAI OAuth 会话暴露为本机 API 或 CLI，例如 Hermes Agent、progrok、grokbuild-proxy 和 grok-oauth-proxy。

所以这个项目没有再去做账号系统。它补的是 Codex 的视频生产层：

- Codex Skill 判断文生视频还是图生视频；
- 生成前确定提示词、时长、比例、清晰度和输出路径；
- 通过本机 OAuth 桥提交任务；
- 异步轮询；
- 下载临时视频 URL；
- 保存任务元数据；
- 用 `ffprobe` 或文件检查确认 MP4 真正可用；
- 把本地素材交给后续剪辑工作流。

最简路线是 `progrok`：

```bash
npm install -g progrok
progrok login
progrok video "一架红色纸飞机在蓝色影棚中滑翔"
```

项目同时保留了经过实际验证的 Hermes 路线。Hermes 方案更适合还想把 Grok Build 作为 Codex 自定义 Agent 的用户，但需要处理 Codex `/responses` 与 xAI 的字段兼容。

## 自动化前后

以前：

```text
Codex → 复制提示词 → 打开 Grok → 上传首帧 → 等待
→ 下载 → 找文件 → 交回 Codex → 剪辑
```

现在：

```text
告诉 Codex“把这一镜做出来”
→ 自动生成 → 自动下载 → 自动质检 → 自动进入剪辑
```

## 它不是什么

这不是免费 API，也不是配额绕过工具。

- 请求仍然消耗账号对应的订阅次数或额度；
- 只能使用自己持有并获准自动化操作的账号；
- OAuth 凭据只应保存在本机；
- 本机代理不能暴露到公网；
- 这是非官方社区兼容方案，xAI 或桥接工具更新后可能失效；
- 使用者需要自行确认服务条款。

## 为什么开源

真正浪费时间的往往不是模型能力，而是模型之间没有连起来。这个项目希望把最常见的网页复制、上传、等待、下载和重新导入压缩成一个可以审计、恢复和验证的本地步骤。

仓库提供 Codex Plugin、Skill、统一视频脚本、Hermes 兼容补丁、双语文档和安全说明。

如果你也同时订阅了 Codex 和 SuperGrok，并且视频工作流卡在两个产品之间，希望这套方案能少让你做几次“人肉 API”。

项目地址：https://github.com/13111655587xl-jpg/codex-grok-video-pipeline
