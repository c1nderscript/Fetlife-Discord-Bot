#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

EVENTS = [{"id": "1", "title": "Test Event"}]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/events'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(EVENTS).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    HTTPServer(('', 8000), Handler).serve_forever()
