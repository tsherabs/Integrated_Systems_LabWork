
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "1.0.0")
STUDENT_ID = os.environ.get("STUDENT_ID", "02230126")
FEATURE_PINNED = os.environ.get("FEATURE_PINNED", "false").lower() == "true"
START_TIME = time.monotonic()

NOTICES = [
    {"id": 1, "title": "Examination Schedule Released"},
    {"id": 2, "title": "Library Opening Hours Updated"},
    {"id": 3, "title": "Campus Sports Event"}
]


class NoticeBoardHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/version":
            self.send_json(200, {
                "version": VERSION,
                "student": STUDENT_ID,
                "pod": os.environ.get("HOSTNAME", os.uname().nodename)
            })

        elif self.path == "/healthz":
            elapsed = time.monotonic() - START_TIME

            if VERSION == "1.2.0-broken":
                self.send_json(503, {"status": "unhealthy"})
            elif elapsed < 5:
                self.send_json(503, {"status": "warming-up"})
            else:
                self.send_json(200, {"status": "healthy"})

        elif self.path == "/notices":
            if VERSION == "1.0.0":
                self.send_json(200, {"notices": NOTICES})
                return

            notices = [
                {**NOTICES[0], "category": "academic", "pinned": False},
                {**NOTICES[1], "category": "facilities", "pinned": False},
                {**NOTICES[2], "category": "events", "pinned": True}
            ]

            if FEATURE_PINNED:
                notices.sort(
                    key=lambda notice: notice["pinned"],
                    reverse=True
                )

            self.send_json(200, {
                "notices": notices,
                "pinnedFirst": FEATURE_PINNED
            })

        else:
            self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("0.0.0.0", 8080),
        NoticeBoardHandler
    )
    print(f"Notice Board {VERSION} running on port 8080", flush=True)
    server.serve_forever()
