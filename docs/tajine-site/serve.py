#!/usr/bin/env python3
"""
TAJINE Documentation Server
===========================
Simple HTTP server to serve the documentation site.
Accessible via Tailscale at: http://localhost:8080
"""

import http.server
import os
import socketserver
import sys

PORT = 8888
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers for local development
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                 TAJINE Documentation Server                ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Local:     http://localhost:8888                         ║
║  Tailscale: http://localhost:8888                      ║
║                                                           ║
║  Press Ctrl+C to stop the server                          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")

    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
