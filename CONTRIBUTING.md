# Contributing

Contributions that improve Codex workflow reliability, media validation, documentation, and compatibility with legitimate local OAuth bridges are welcome.

Out of scope:

- credential collection, account creation, or credential pooling;
- hosted public proxies;
- quota, rate-limit, payment, or product-restriction bypasses;
- committing captured OAuth material or private generated media.

Before opening a pull request:

```bash
python3 -m py_compile skills/grok-imagine-video/scripts/grok_video.py
python3 -m unittest discover -s tests -v
python3 /path/to/quick_validate.py skills/grok-imagine-video
python3 /path/to/validate_plugin.py .
```

For upstream protocol changes, include a redacted reproducible response shape, the bridge and model versions, and a test that does not require contributors to expose credentials.
