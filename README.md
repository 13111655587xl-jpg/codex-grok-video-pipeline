# Codex Grok Video Pipeline

[简体中文](README.zh-CN.md)

Turn Codex plus your own SuperGrok subscription into a local, end-to-end AI video workflow:

```text
script → first frame → motion prompt → Grok Imagine → local MP4 → QC → editing
```

This project packages the missing bridge as a Codex plugin and skill. Codex can submit text-to-video or image-to-video jobs, wait for completion, download the result, retain metadata, verify the media, and hand it to the next editing step—without the usual browser copy/upload/download loop.

> [!IMPORTANT]
> This is an unofficial community interoperability project. It is not affiliated with or endorsed by OpenAI, xAI, Grok, Nous Research, Hermes Agent, or progrok. It does not bypass quotas or product limits. Use only an account you own, review the applicable terms, and expect subscription usage to be consumed.

## Why

The common workflow is surprisingly manual: Codex writes the script and prompt, the user opens Grok, uploads a first frame, pastes the prompt, waits, downloads the result, and gives the file back to Codex for editing. This plugin turns that human relay into a reproducible local workflow.

## Backends

The bundled command supports two local OAuth bridges:

| Backend | Recommended for | Setup |
| --- | --- | --- |
| `progrok` | The shortest installation and direct video CLI | `npm install -g progrok && progrok login` |
| `hermes` | A verified Hermes OAuth proxy and Codex Responses compatibility path | See [Hermes advanced setup](docs/hermes-advanced.md) |

`auto` prefers `progrok` when installed, otherwise it checks the Hermes proxy at `http://127.0.0.1:8645/v1`.

## Quick start

### 1. Install and authenticate a local bridge

Shortest route:

```bash
npm install -g progrok
progrok login
progrok status
```

OAuth credentials remain in the bridge's local credential store. This plugin never reads or prints them.

### 2. Install the Codex skill

```bash
git clone https://github.com/13111655587xl-jpg/codex-grok-video-pipeline.git
mkdir -p "$HOME/.agents/skills"
cp -R codex-grok-video-pipeline/skills/grok-imagine-video "$HOME/.agents/skills/"
```

Restart Codex so it discovers the skill. The repository also contains a validated `.codex-plugin/plugin.json` for local plugin development and future marketplace packaging.

### 3. Ask Codex

```text
Create a 5-second 16:9 Grok Imagine video of a red paper airplane
gliding through a blue studio. Save it under ./output and verify it.
```

Or run the wrapper directly:

```bash
python3 skills/grok-imagine-video/scripts/grok_video.py generate \
  --prompt "A red paper airplane glides through a clean blue studio" \
  --duration 5 --aspect-ratio 16:9 --resolution 480p \
  --output "$PWD/output/paper-airplane.mp4"
```

Image-to-video:

```bash
python3 skills/grok-imagine-video/scripts/grok_video.py generate \
  --image "$PWD/first-frame.png" \
  --prompt "Subtle natural motion, slow camera push-in" \
  --duration 5 --aspect-ratio 16:9 --resolution 720p \
  --output "$PWD/output/shot-01.mp4"
```

Validate arguments without submitting a quota-consuming job:

```bash
python3 skills/grok-imagine-video/scripts/grok_video.py generate \
  --prompt "test" --output "$PWD/output/test.mp4" --dry-run
```

## What the skill enforces

- An explicit, absolute output path.
- No direct reading of OAuth stores or token construction.
- Async polling and local download for the Hermes backend.
- A metadata sidecar for Hermes jobs, enabling interrupted-job resume.
- Non-empty MP4 verification and optional `ffprobe` inspection.
- No delivery claim until the local media file exists.
- Loopback-only proxy guidance.

## Security

- Keep every OAuth bridge bound to `127.0.0.1`.
- Never commit auth files, refresh tokens, logs containing credentials, or generated private media.
- Do not operate shared credential pools or resell subscription access.
- Treat upstream protocol behavior as unstable and pin versions for production workflows.

See [SECURITY.md](SECURITY.md) and [DISCLAIMER.md](DISCLAIMER.md).

## Project scope

This repository is intentionally the Codex workflow layer, not another account farm or hosted proxy. Existing bridges handle OAuth. The value here is reliable orchestration from creative planning through a verified local video artifact and onward to editing.

## Compatibility

The original Hermes route was verified on macOS ARM with Codex `0.147.0-alpha.6.5`, Hermes Agent `0.20.0`, and `grok-imagine-video-1.5`. Community tools and xAI endpoints can change without notice; the included smoke tests do not consume generation quota.

## Documentation

- [Architecture](docs/architecture.md)
- [Hermes advanced setup](docs/hermes-advanced.md)
- [Publishing story / article](docs/article.zh-CN.md)
- [Disclaimer](DISCLAIMER.md)

## License

MIT. Third-party projects and services retain their own licenses, terms, and trademarks.
