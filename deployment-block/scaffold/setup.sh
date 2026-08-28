#!/usr/bin/env bash
# One-time setup, run ON the device (Dragonwing IQ-9075 / IQ-8275 EVK or other
# Snapdragon Linux board). Needs network access for the downloads below.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/4 GenieX CLI"
if ! command -v geniex >/dev/null 2>&1; then
    curl -fsSL https://qaihub-public-assets.s3.us-west-2.amazonaws.com/qai-hub-geniex/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
geniex --version

echo "==> 2/4 Python dependencies"
python3 -m pip install --user -r requirements.txt
# opencv on aarch64 boards: prefer the distro package if pip has no wheel
python3 -c "import cv2" 2>/dev/null || sudo apt-get install -y python3-opencv || true

echo "==> 3/4 Edge Impulse impulse (.eim)"
if ! command -v edge-impulse-linux-runner >/dev/null 2>&1; then
    npm install -g edge-impulse-linux
fi
if [ ! -f model.eim ]; then
    # Logs into your Edge Impulse account, builds the impulse for this device
    # (NPU-accelerated where supported), and saves it as model.eim
    edge-impulse-linux-runner --download model.eim
fi

echo "==> 4/4 GenieX model (from config.yaml)"
MODEL="$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['geniex']['model'])")"
geniex pull "$MODEL"

echo ""
echo "Setup complete. Start the agent with:  bash run.sh"
