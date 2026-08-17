#!/usr/bin/env python3
"""Generate and verify Grok Imagine videos through a local OAuth bridge."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


HERMES_BASE_URL = "http://127.0.0.1:8645/v1"
DEFAULT_MODEL = "grok-imagine-video-1.5"
MAX_INLINE_IMAGE_BYTES = 7_000_000


class APIError(RuntimeError):
    def __init__(self, status: int, message: str, body: Any = None) -> None:
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message
        self.body = body


def hermes_base_url() -> str:
    return os.environ.get("GROK_IMAGINE_PROXY_URL", HERMES_BASE_URL).rstrip("/")


def decode_json(raw: bytes) -> Any:
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text[:2000]}


def error_message(data: Any) -> str:
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            return str(error.get("message") or error.get("error") or error)
        return str(error or data.get("message") or data)
    return str(data)


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = urllib.request.Request(
        hermes_base_url() + path,
        data=data,
        method=method,
        headers={
            "Authorization": "Bearer local-codex-placeholder",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return decode_json(response.read())
    except urllib.error.HTTPError as exc:
        body = decode_json(exc.read())
        raise APIError(exc.code, error_message(body), body) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Cannot reach the Hermes proxy at {hermes_base_url()}: {exc.reason}"
        ) from exc


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def metadata_path_for(output: Path) -> Path:
    return output.with_suffix(output.suffix + ".json")


def media_source(value: str) -> dict[str, str]:
    if value.startswith(("https://", "http://", "data:")):
        return {"url": value}
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"Image not found: {path}")
    if path.stat().st_size > MAX_INLINE_IMAGE_BYTES:
        raise ValueError("Local image exceeds 7 MB; compress it or use a public URL")
    mime, _ = mimetypes.guess_type(path.name)
    if mime not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Image must be JPEG, PNG, or WebP")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"url": f"data:{mime};base64,{encoded}"}


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    clone = json.loads(json.dumps(payload))
    image = clone.get("image")
    if isinstance(image, dict) and str(image.get("url", "")).startswith("data:"):
        image["url"] = "<inline-image-redacted>"
    return clone


def resolve_backend(requested: str) -> str:
    if requested != "auto":
        return requested
    if shutil.which("progrok"):
        return "progrok"
    return "hermes"


def validate_output(output: Path) -> dict[str, Any]:
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"Video output is missing or empty: {output}")
    result: dict[str, Any] = {
        "output": str(output),
        "output_bytes": output.stat().st_size,
    }
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        result["ffprobe"] = "not installed; non-empty file check passed"
        return result
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "stream=codec_name,width,height,r_frame_rate",
        "-show_entries",
        "format=duration,size",
        "-of",
        "json",
        str(output),
    ]
    checked = subprocess.run(command, capture_output=True, text=True, check=False)
    if checked.returncode != 0:
        raise RuntimeError(f"ffprobe rejected the downloaded video: {checked.stderr.strip()}")
    result["media_probe"] = json.loads(checked.stdout)
    return result


def download_video(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "codex-grok-video/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open(
            "wb"
        ) as target:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                target.write(chunk)
        if temporary.stat().st_size == 0:
            raise RuntimeError("Downloaded video is empty")
        os.replace(temporary, output)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def poll_hermes(
    request_id: str,
    *,
    output: Path,
    metadata_path: Path,
    metadata: dict[str, Any],
    timeout: int,
    interval: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while True:
        result = request_json("GET", f"/videos/{request_id}")
        if not isinstance(result, dict):
            raise RuntimeError(f"Unexpected status response: {result!r}")
        status = str(result.get("status", "unknown"))
        metadata.update(
            {"status": status, "last_response": result, "updated_at": int(time.time())}
        )
        atomic_json(metadata_path, metadata)
        if status == "done":
            video = result.get("video") or {}
            url = video.get("url") if isinstance(video, dict) else None
            if not url:
                raise RuntimeError("Completed response has no video URL")
            download_video(str(url), output)
            metadata.update(validate_output(output))
            metadata["downloaded_at"] = int(time.time())
            atomic_json(metadata_path, metadata)
            return metadata
        if status in {"failed", "expired"}:
            raise RuntimeError(f"Video request {status}: {result}")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out; resume using metadata: {metadata_path}")
        time.sleep(interval)


def generate_progrok(args: argparse.Namespace, output: Path) -> dict[str, Any]:
    installed = shutil.which("progrok")
    if not installed and not args.dry_run:
        raise RuntimeError("progrok is not installed; run `npm install -g progrok`")
    executable = installed or "progrok"
    command = [
        executable,
        "video",
        args.prompt,
        "--duration",
        str(args.duration),
        "--aspect",
        args.aspect_ratio,
        "--resolution",
        args.resolution,
        "--output",
        str(output),
    ]
    if args.image:
        command.extend(["--image", args.image])
    if args.model:
        command.extend(["--model", args.model])
    if args.dry_run:
        return {"backend": "progrok", "command": command, "dry_run": True}
    output.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"progrok exited with status {completed.returncode}")
    result = {"backend": "progrok", "status": "done", "request": command[2:]}
    result.update(validate_output(output))
    return result


def generate_hermes(args: argparse.Namespace, output: Path) -> dict[str, Any]:
    metadata_path = (
        Path(args.metadata).expanduser().resolve()
        if args.metadata
        else metadata_path_for(output)
    )
    payload: dict[str, Any] = {
        "model": args.model or DEFAULT_MODEL,
        "duration": args.duration,
        "aspect_ratio": args.aspect_ratio,
        "resolution": args.resolution,
        "prompt": args.prompt,
    }
    if args.image:
        payload["image"] = media_source(args.image)
    if args.dry_run:
        return {
            "backend": "hermes",
            "url": hermes_base_url() + "/videos/generations",
            "request": redact_payload(payload),
            "dry_run": True,
        }
    submitted = request_json("POST", "/videos/generations", payload)
    if not isinstance(submitted, dict) or not submitted.get("request_id"):
        raise RuntimeError(f"Generation did not return request_id: {submitted!r}")
    request_id = str(submitted["request_id"])
    metadata: dict[str, Any] = {
        "backend": "hermes",
        "request_id": request_id,
        "status": "submitted",
        "submitted_at": int(time.time()),
        "request": redact_payload(payload),
        "output": str(output),
        "metadata": str(metadata_path),
    }
    atomic_json(metadata_path, metadata)
    if args.no_wait:
        return metadata
    return poll_hermes(
        request_id,
        output=output,
        metadata_path=metadata_path,
        metadata=metadata,
        timeout=args.timeout,
        interval=args.poll_interval,
    )


def cmd_generate(args: argparse.Namespace) -> int:
    output = Path(args.output).expanduser().resolve()
    backend = resolve_backend(args.backend)
    if backend == "progrok" and args.no_wait:
        raise ValueError("--no-wait is only supported by the Hermes backend")
    result = (
        generate_progrok(args, output)
        if backend == "progrok"
        else generate_hermes(args, output)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    metadata_path = Path(args.metadata).expanduser().resolve()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    request_id = metadata.get("request_id")
    output_value = args.output or metadata.get("output")
    if not request_id or not output_value:
        raise ValueError("Metadata must contain request_id and output")
    output = Path(output_value).expanduser().resolve()
    if args.wait:
        result = poll_hermes(
            str(request_id),
            output=output,
            metadata_path=metadata_path,
            metadata=metadata,
            timeout=args.timeout,
            interval=args.poll_interval,
        )
    else:
        response = request_json("GET", f"/videos/{request_id}")
        metadata.update({"status": response.get("status"), "last_response": response})
        atomic_json(metadata_path, metadata)
        result = metadata
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    backend = resolve_backend(args.backend)
    if backend == "progrok":
        executable = shutil.which("progrok")
        if not executable:
            raise RuntimeError("progrok is not installed")
        completed = subprocess.run([executable, "status"], check=False)
        if completed.returncode != 0:
            raise RuntimeError("progrok status did not report a usable session")
        print("PROBE_OK: progrok is installed and reports a usable local session")
        return 0
    try:
        request_json("POST", "/videos/generations", {})
    except APIError as exc:
        if exc.status == 400 and "prompt" in exc.message.lower():
            print("PROBE_OK: Hermes OAuth reached the xAI video endpoint")
            return 0
        raise
    raise RuntimeError("Probe unexpectedly accepted an empty request")


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="Generate and download a video")
    generate.add_argument("--backend", choices=("auto", "progrok", "hermes"), default="auto")
    generate.add_argument("--prompt", required=True)
    generate.add_argument("--image", help="Local JPEG/PNG/WebP path or URL")
    generate.add_argument("--output", required=True)
    generate.add_argument("--metadata", help="Hermes metadata JSON path")
    generate.add_argument("--model", help="Override the backend's video model")
    generate.add_argument("--duration", type=int, default=5, choices=range(1, 16))
    generate.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=("1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"),
    )
    generate.add_argument(
        "--resolution", default="480p", choices=("480p", "720p", "1080p")
    )
    generate.add_argument("--timeout", type=int, default=900)
    generate.add_argument("--poll-interval", type=float, default=5.0)
    generate.add_argument("--no-wait", action="store_true")
    generate.add_argument("--dry-run", action="store_true")
    generate.set_defaults(func=cmd_generate)

    status = commands.add_parser("status", help="Inspect or resume a Hermes job")
    status.add_argument("--metadata", required=True)
    status.add_argument("--output")
    status.add_argument("--wait", action="store_true")
    status.add_argument("--timeout", type=int, default=900)
    status.add_argument("--poll-interval", type=float, default=5.0)
    status.set_defaults(func=cmd_status)

    probe = commands.add_parser("probe", help="Check local OAuth bridge access")
    probe.add_argument("--backend", choices=("auto", "progrok", "hermes"), default="auto")
    probe.set_defaults(func=cmd_probe)
    return root


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except (APIError, RuntimeError, ValueError, TimeoutError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
