#!/usr/bin/env python3
"""Local preview server for the Kiwi Nails site."""
import http.server
import os
import socketserver
import sys

PORT = int(os.environ.get("PORT", 8766))
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"Serving on http://127.0.0.1:{PORT}")
    httpd.serve_forever()
