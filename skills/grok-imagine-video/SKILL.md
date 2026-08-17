---
name: grok-imagine-video
description: Generate, download, verify, and resume Grok Imagine text-to-video or image-to-video jobs through the user's local SuperGrok OAuth bridge. Use when the user asks Codex for a Grok Imagine MP4, an animated first frame, video status, or a locally delivered generated clip.
---

# Grok Imagine Video

Use `scripts/grok_video.py`. Never read OAuth credential files or construct upstream OAuth headers.

## Before generation

1. Choose an explicit absolute `.mp4` output path inside the user's intended workspace.
2. State the prompt, input image if any, duration, aspect ratio, resolution, output path, and backend.
3. Explain that a real submission may consume subscription quota. Use `--dry-run` when the user only wants validation.

## Generate

```bash
python3 <skill-dir>/scripts/grok_video.py generate \
  --backend auto \
  --prompt "A paper crane flying over a moonlit lake" \
  --duration 5 --aspect-ratio 16:9 --resolution 720p \
  --output /absolute/path/crane.mp4
```

For image-to-video, add `--image /absolute/path/input.png`.

Backend behavior:

- `auto`: prefer an installed `progrok`; otherwise use the Hermes proxy.
- `progrok`: call the installed `progrok video` CLI. It handles polling and download.
- `hermes`: submit through `GROK_IMAGINE_PROXY_URL` or `http://127.0.0.1:8645/v1`, retain `<output>.json`, poll, and download.

## Resume Hermes jobs

```bash
python3 <skill-dir>/scripts/grok_video.py status \
  --metadata /absolute/path/video.mp4.json --wait
```

Do not resubmit an interrupted job when a metadata sidecar already contains a request ID.

## Deliver

- Confirm that the MP4 exists and is non-empty.
- Report the absolute MP4 path, backend, model, requested duration/resolution, and metadata path when present.
- If `ffprobe` is installed, report its media summary.
- Never present a submitted or pending job as complete.
- Do not expose OAuth material or temporary remote video URLs.
