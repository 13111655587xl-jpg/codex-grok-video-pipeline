# Advanced: Hermes OAuth proxy

This route was validated with Hermes Agent `0.20.0`. It is retained for users who want one local bridge for both a Codex Grok Build custom agent and Grok Imagine video jobs.

> Hermes internals and xAI behavior can change. Review the patch before applying it to any other version. Do not replace newer Hermes files with old copies.

## 1. Authenticate

```bash
hermes auth add xai-oauth --type oauth
hermes auth list
hermes proxy status
```

## 2. Apply the versioned patch

From the Hermes checkout:

```bash
git apply --check /absolute/path/to/patches/hermes-0.20.0-codex-video.patch
git apply /absolute/path/to/patches/hermes-0.20.0-codex-video.patch
```

The patch:

- adds video generation/edit/extension routes;
- restricts dynamic status polling to `/videos/<UUID>`;
- removes Codex-only `namespace` tools and `external_web_access` from xAI `/responses` payloads;
- lets `aiohttp` honor `HTTP_PROXY` and `HTTPS_PROXY` when needed.

## 3. Start locally

```bash
hermes proxy start --provider xai --host 127.0.0.1 --port 8645
curl http://127.0.0.1:8645/health
```

Expected shape:

```json
{"status":"ok","upstream":"xAI Grok OAuth","authenticated":true}
```

Never use `--host 0.0.0.0`.

## 4. Probe without a valid generation prompt

```bash
python3 skills/grok-imagine-video/scripts/grok_video.py probe --backend hermes
```

The probe expects the upstream to reject an empty generation request with an HTTP 400 prompt validation error. It must not return 401/403.

## 5. Optional Codex provider

Add this only to the user-level `~/.codex/config.toml`:

```toml
[model_providers.xai]
name = "xAI via local Hermes OAuth"
base_url = "http://127.0.0.1:8645/v1"
experimental_bearer_token = "local-placeholder"
wire_api = "responses"
supports_websockets = false
```

The placeholder is not an xAI API key. Hermes replaces it locally.

## 6. Network-restricted environments

The patch enables `trust_env=True`. Only when direct xAI access is unavailable, set the correct local proxy values before starting Hermes:

```bash
export HTTP_PROXY="http://127.0.0.1:<port>"
export HTTPS_PROXY="http://127.0.0.1:<port>"
export NO_PROXY="localhost,127.0.0.1,::1"
```

Do not copy another person's proxy port blindly.
