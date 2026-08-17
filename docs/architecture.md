# Architecture

## Recommended path

```text
User request
    ↓
Codex creative and production workflow
    ↓
grok-imagine-video skill
    ↓
grok_video.py
    ↓
progrok CLI → local xAI OAuth session → xAI video endpoints
    ↓
downloaded MP4 → ffprobe/non-empty validation → editing workflow
```

The recommended path does not require Grok to be the Codex reasoning model. Codex remains the orchestrator and invokes the video generator as a local tool. This is the smallest solution for the actual media-production problem.

## Advanced Hermes path

```text
Codex / optional grok_builder agent
    ↓
http://127.0.0.1:8645/v1
    ↓
patched Hermes xAI OAuth proxy
    ├── /responses
    └── /videos/*
    ↓
xAI Grok Build / Imagine
```

The advanced path is useful when the same OAuth bridge must serve both a Grok Build custom agent and video generation. It requires a version-sensitive Hermes patch.

## Trust boundaries

1. The Codex plugin never reads the OAuth store.
2. The local bridge owns OAuth refresh and bearer injection.
3. The wrapper sends only a placeholder client bearer to Hermes.
4. Temporary upstream video URLs are downloaded immediately and not presented as the final artifact.
5. Local proxies must remain loopback-only.

## Why a skill instead of a model provider alone

Video generation is an asynchronous media job, not a conversational model turn. A skill can express the operational contract that a generic provider cannot: output paths, quota warning, polling, sidecar metadata, download, media validation, and handoff to editing.
