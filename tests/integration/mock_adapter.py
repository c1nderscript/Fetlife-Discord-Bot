#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

EVENTS = [{"id": "1", "title": "Test Event"}]
GROUP_POSTS = [
    {
        "id": 3,
        "title": "Group Topic",
        "link": "https://fetlife.com/groups/1/group_posts/3",
        "published": "2024-03-01T00:00:00Z",
    }
]
MESSAGES = [
    {
        "id": 1,
        "sender": "alice",
        "text": "hello",
        "sent": "2025-08-12T00:00:00Z",
    }
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/events"):
            body = EVENTS
        elif self.path.startswith("/groups") and self.path.endswith("/posts"):
            body = GROUP_POSTS
        elif self.path.startswith("/messages"):
            body = MESSAGES
        else:
            body = None
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    HTTPServer(("", 8000), Handler).serve_forever()
