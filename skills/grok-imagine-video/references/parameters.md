# Parameters

The wrapper currently exposes the common, verified intersection:

- Model: backend default or `--model`
- Duration: 1–15 seconds
- Aspect ratios: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`
- Resolution: `480p`, `720p`, `1080p`
- Text-to-video: `--prompt`
- Image-to-video: `--prompt` plus `--image`

Model availability and limits are account- and time-dependent. Prefer a low-resolution, short smoke test before a production batch. A successful submission is not a deliverable until the local MP4 downloads and passes verification.

Official xAI references:

- https://docs.x.ai/developers/model-capabilities/video/generation
- https://docs.x.ai/developers/model-capabilities/video/image-to-video
- https://docs.x.ai/developers/rest-api-reference/inference/videos
