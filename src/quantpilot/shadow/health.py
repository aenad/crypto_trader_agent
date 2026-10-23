import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .feed import WallClock
from .service import health
from .storage import ShadowStore


class HealthServer:
    def __init__(self, store: ShadowStore, port: int):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path != "/health":
                    self.send_error(404)
                    return
                try:
                    result = health(store, WallClock().now())
                    code = 200 if result["status"] == "HEALTHY" else 503
                except Exception:
                    result = {"status": "UNAVAILABLE", "exchange_mutations": "BLOCKED"}
                    code = 503
                body = json.dumps(result, sort_keys=True).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:
                # Drain only small, bounded bodies before closing. Otherwise
                # Windows can reset the socket before the 405 reaches the client.
                self.connection.settimeout(2)
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if 0 < size <= 4096:
                        self.rfile.read(size)
                except (ValueError, OSError):
                    pass
                self.send_error(405)

            def log_message(self, format: str, *args: Any) -> None:
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> "HealthServer":
        self.thread.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
