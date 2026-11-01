"""Tiny dependency-free HTTP service used for the COMP3104 Assignment 2 pipeline."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 (name required by BaseHTTPRequestHandler)
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        elif self.path == "/":
            self._send(
                200,
                {
                    "message": "Hello from COMP3104 Assignment 2",
                    "version": os.environ.get("APP_VERSION", "dev"),
                },
            )
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        # One JSON object per line: easy to read with `docker logs` and to ship to ELK later.
        print(json.dumps({"event": "request", "detail": fmt % args}), flush=True)


def create_server(port=0):
    return HTTPServer(("0.0.0.0", port), Handler)


def main():
    port = int(os.environ.get("PORT", "3000"))
    print(json.dumps({"event": "startup", "port": port}), flush=True)
    create_server(port).serve_forever()


if __name__ == "__main__":
    main()
