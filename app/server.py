"""
server.py — Simple HTTP server for the web profile demo.
Serves static files and exposes a /server-info JSON endpoint
so students can see which container is handling each request.
"""

import http.server
import json
import os
import socket
import socketserver
from pathlib import Path

PORT = int(os.environ.get("PORT", 8080))
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "unknown")
STATIC_DIR = Path(__file__).parent / "static"


class ProfileHandler(http.server.SimpleHTTPRequestHandler):
    """Serve static files from ./static and handle /server-info."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/server-info":
            self._serve_server_info()
        elif self.path == "/health":
            self._serve_health()
        else:
            super().do_GET()

    def _serve_server_info(self):
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except Exception:
            ip = "unknown"

        payload = json.dumps({
            "container": CONTAINER_NAME,
            "hostname": hostname,
            "ip": ip,
            "port": PORT,
        }).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _serve_health(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, fmt, *args):
        print(f"[{CONTAINER_NAME}] {fmt % args}")


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ProfileHandler) as httpd:
        print(f"[{CONTAINER_NAME}] Serving on port {PORT} ...")
        httpd.serve_forever()
