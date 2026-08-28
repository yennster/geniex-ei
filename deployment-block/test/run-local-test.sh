#!/usr/bin/env bash
# Local end-to-end test of the deployment block, no device or EI account needed:
#   1. run the generator against mock metadata, inspect deploy.zip
#   2. fire the generated app's --mock path against a stub OpenAI server
set -euo pipefail
cd "$(dirname "$0")/.."    # deployment-block/

OUT=test/output
rm -rf "$OUT"
mkdir -p "$OUT"

echo "== 1. generator =="
python3 - <<'PY'
import json
m = json.load(open('test/mock-input/deployment-metadata.json'))
m['folders']['output'] = 'test/output'
json.dump(m, open('test/output/metadata-local.json', 'w'), indent=2)
PY
python3 build.py --metadata test/output/metadata-local.json
unzip -o -q "$OUT/deploy.zip" -d "$OUT/unzipped"
echo "--- deploy.zip contents:"
(cd "$OUT/unzipped" && find . -type f | sort)

echo ""
echo "== 2. syntax check the generated app =="
python3 -m py_compile "$OUT/unzipped/agent.py"
echo "agent.py compiles OK"

echo ""
echo "== 3. mock run against stub server =="
if [ ! -d "$OUT/venv" ]; then
    python3 -m venv "$OUT/venv"
    "$OUT/venv/bin/pip" -q install openai pyyaml
fi

"$OUT/venv/bin/python" test/test_trigger_policy.py

# tiny test image (PNG bytes; converted to real JPEG via sips when available)
python3 - <<'PY'
import struct, zlib
w = h = 8
def chunk(t, d):
    c = t + d
    return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
raw = b''.join(b'\x00' + b'\xd0\x3c\x14' * w for _ in range(h))
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(raw))
       + chunk(b'IEND', b''))
open('test/output/test.png', 'wb').write(png)
PY
if command -v sips >/dev/null 2>&1; then
    sips -s format jpeg "$OUT/test.png" --out "$OUT/test.jpg" >/dev/null
else
    cp "$OUT/test.png" "$OUT/test.jpg"   # stub never decodes it
fi

python3 test/stub_openai_server.py &
STUB_PID=$!
trap 'kill $STUB_PID 2>/dev/null || true' EXIT
sleep 1

(cd "$OUT/unzipped" && ../venv/bin/python agent.py --mock --image ../test.jpg)

echo ""
echo "== 4. events log =="
cat "$OUT/unzipped/events.jsonl"
echo ""
echo "ALL LOCAL TESTS PASSED"
