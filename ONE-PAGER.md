# GenieX × Edge Impulse — Integration One-Pager

**Author:** Jenny Speelman · **Date:** August 28, 2026 · **Status:** working prototype (local validation done, device validation pending)

## The opportunity

[GenieX](https://github.com/qualcomm/GenieX) is Qualcomm's open-source on-device LLM/VLM runtime (the community version of GENIE): any GGUF from Hugging Face via llama.cpp, or pre-compiled Qualcomm AI Hub bundles via QAIRT, running on the Hexagon NPU. Edge Impulse builds the *other* half of edge AI: tiny always-on sensor models, trained and deployed from Studio. Both are Qualcomm products, and both validate on the same hardware — **Dragonwing IQ-9075 / IQ-8275 EVKs** (Linux), Snapdragon X (Windows), Snapdragon 8 Elite (Android).

Together they complete the **cascade pattern**: the milliwatt-class Edge Impulse model watches the sensor forever, and wakes a local LLM/VLM only when something matters. No cloud, no per-token cost, no data leaving the device.

## Key technical facts (verified in the GenieX source)

- **OpenAI-compatible local server** (`geniex serve`, port 18181): chat completions with `image_url` vision parts, `tools` function calling, a `/v1/logits` endpoint, and configurable CORS origins. Anything that speaks OpenAI speaks GenieX.
- **Audio input** works on the llama.cpp path (e.g. Gemma-4's conformer audio encoder) — one turn can mix text + image + audio.
- **Snapdragon-only** (no x86): GenieX cannot run in Edge Impulse's cloud, so every integration runs on the user's own silicon — which *is* the pitch: private, free, offline.

## Integration directions

| # | Direction | Shape | Status |
|---|-----------|-------|--------|
| 1 | **GenieX agent app deployment block** | Studio Deployment option emitting a ready-to-run Python app: impulse on NPU → trigger policy → local VLM assessment → log/webhook | **Prototype built** |
| 2 | Local NPU data labeling | The existing GPT-4o labeling block pattern with `baseURL` pointed at a local GenieX server — label datasets on a Snapdragon laptop, no API bill | Scoped |
| 3 | Studio labeling extension | Iframe extension calling the user's local GenieX server for human-in-the-loop labeling | Scoped |
| 4 | Closed active-learning loop | VLM pre-labels → tiny model trains → deploys with GenieX sidecar → low-confidence samples re-labeled on-device and re-ingested | Flagship narrative, builds on 1+2 |

## What exists today (`deployment-block/`)

A custom deployment block that reads `deployment-metadata.json` and generates a project-specific app: real class names baked into prompts, background classes auto-ignored, trigger policy (confidence bar, debounce, cooldown) gating calls to GenieX. The zip ships the app only — the NPU-accelerated `.eim` is fetched on-device by `edge-impulse-linux-runner --download`, so the block never cross-compiles. The LLM side is pure OpenAI protocol, so prompt iteration works on any machine (`agent.py --mock` against any OpenAI-compatible server).

**Verified locally:** generator output, trigger-policy unit tests (6), and the exact request wire-shape GenieX's server parses (text + base64 JPEG `image_url`), via a validating stub server.

## Next steps

1. Run the block via `edge-impulse-blocks runner` against a real project (needs a Docker runtime) and push to the org.
2. Validate on hardware: IQ-9075 EVK or a Qualcomm Device Cloud session — GenieX install, Gemma-4 pull, real NPU inference end to end.
3. Then: audio variant, impulse-as-`tool` for on-demand sensing, and the closed-loop demo as a blog/tutorial.
