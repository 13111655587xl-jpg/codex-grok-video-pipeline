# Security Policy

## Non-negotiable boundary

Run OAuth bridges on loopback only (`127.0.0.1`). A bridge that injects an OAuth bearer may accept a placeholder client token; exposing that listener to a LAN or the public internet can expose the account behind it.

## Never commit

- OAuth access or refresh tokens
- `auth.json`, `.env`, token caches, or browser profiles
- generated media that contains private or identifying material
- debug logs containing request headers
- signed temporary download or upload URLs

The repository `.gitignore` covers common cases, but users remain responsible for inspecting every commit.

## Reporting

Open a GitHub security advisory for vulnerabilities that could disclose credentials or bypass the loopback boundary. Do not paste live credentials into issues.

## Supported versions

Only the latest tagged release is supported. OAuth and upstream API behavior can change independently of this repository.
