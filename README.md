# GenieX × Edge Impulse

Explorations in integrating [Qualcomm GenieX](https://github.com/qualcomm/GenieX)
(on-device LLM/VLM runtime for Snapdragon) with [Edge Impulse](https://edgeimpulse.com).
See [ONE-PAGER.md](ONE-PAGER.md) for the integration proposal at a glance.

## deployment-block/

An Edge Impulse **custom deployment block**: "GenieX agent app (Linux)". From the
Studio Deployment page it emits a ready-to-run Python app for Snapdragon Linux
boards (validated targets shared by both products: Dragonwing IQ-9075 / IQ-8275
EVK) where:

1. the project's impulse runs continuously on the NPU (`.eim` via the Edge
   Impulse Linux runner — downloaded on-device, so the block never cross-compiles),
2. a trigger policy (watched classes, confidence bar, debounce, cooldown) decides
   when something interesting happened,
3. the detection + camera frame go to a local LLM/VLM behind GenieX's
   OpenAI-compatible server (`geniex serve`, port 18181),
4. the model's assessment is printed, logged to JSONL, and optionally POSTed to a
   webhook.

The cascade pattern: the tiny always-on model gates the expensive model, and
everything stays on the device.

### Test locally (no device, no Edge Impulse account)

```bash
cd deployment-block
bash test/run-local-test.sh
```

This runs the generator against mock metadata, unzips and inspects the result,
and fires the generated app's `--mock` path against a stub OpenAI server that
validates the request shape GenieX would receive.

### Test against a real project

```bash
cd deployment-block
edge-impulse-blocks runner --download-data input/    # fetches real input for one of your projects
docker build -t geniex-agent-block .
docker run --rm -v $PWD:/home geniex-agent-block --metadata /home/input/deployment-metadata.json
```

Then push it to your organization with `edge-impulse-blocks init` + `edge-impulse-blocks push`.

## geniex/

Shallow clone of upstream `qualcomm/geniex` for reference (gitignored).
