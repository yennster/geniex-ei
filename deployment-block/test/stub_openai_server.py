#!/usr/bin/env python3
"""Stub OpenAI-compatible server standing in for `geniex serve` in local tests.

Validates the request shape the agent sends (model, system+user messages,
text part, image_url data URL) and returns a canned chat completion.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 18181


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            self._send(200, {"object": "list", "data": [{"id": "stub-model", "object": "model"}]})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.endswith("/chat/completions"):
            self._send(404, {"error": "not found"})
            return
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))

        problems = []
        if not req.get("model"):
            problems.append("missing model")
        msgs = req.get("messages", [])
        if len(msgs) != 2 or msgs[0].get("role") != "system" or msgs[1].get("role") != "user":
            problems.append(f"unexpected message roles: {[m.get('role') for m in msgs]}")
        content = msgs[1].get("content") if len(msgs) > 1 else []
        kinds = [p.get("type") for p in content] if isinstance(content, list) else ["<str>"]
        has_image = False
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "image_url":
                    url = part.get("image_url", {}).get("url", "")
                    if url.startswith("data:image/jpeg;base64,") and len(url) > 30:
                        has_image = True
                    else:
                        problems.append(f"bad image_url: {url[:40]}...")

        print(
            f"[stub] model={req.get('model')} parts={kinds} "
            f"image={'yes' if has_image else 'no'} "
            f"max_tokens={req.get('max_tokens')} problems={problems or 'none'}",
            file=sys.stderr,
        )
        if problems:
            self._send(400, {"error": "; ".join(problems)})
            return

        self._send(
            200,
            {
                "id": "chatcmpl-stub",
                "object": "chat.completion",
                "model": req["model"],
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": "STUB ASSESSMENT: a person without a hardhat is near "
                            "the loading bay. Needs attention. Recommended action: pause "
                            "the lift and page the site supervisor.",
                        },
                    }
                ],
            },
        )


if __name__ == "__main__":
    print(f"[stub] listening on 127.0.0.1:{PORT}", file=sys.stderr)
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
