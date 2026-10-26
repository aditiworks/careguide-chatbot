"""Local educational web demo. Python standard library only."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from chatbot import reply

ROOT = Path(__file__).parent
MAX_BODY = 12000

class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *args):
        pass

    def send(self, status, body, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def json_response(self, status, data):
        if status >= 400 and self.command == "POST" and not getattr(self, "_body_read", False):
            # Drain a bounded amount before closing: unread bytes can cause a
            # TCP reset on Windows and discard the structured error response.
            self.connection.settimeout(0.1)
            remaining = 65536
            try:
                while remaining:
                    chunk = self.rfile.read1(min(8192, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
            except (TimeoutError, OSError):
                pass
        self.send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def valid_host(self):
        return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def do_GET(self):
        if not self.valid_host():
            return self.json_response(403, {"error": "Invalid host."})
        files = {"/": ("index.html", "text/html"), "/style.css": ("style.css", "text/css"), "/script.js": ("script.js", "text/javascript")}
        if self.path == "/health":
            return self.json_response(200, {"status": "ok"})
        if self.path not in files:
            return self.json_response(404, {"error": "Not found."})
        name, mime = files[self.path]
        self.send(200, (ROOT / "static" / name).read_bytes(), mime + "; charset=utf-8")

    def do_POST(self):
        self.close_connection = True
        port = self.server.server_port
        if not self.valid_host() or self.headers.get("Origin") not in {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}:
            return self.json_response(403, {"error": "Only same-origin requests are accepted."})
        if self.path != "/api/chat":
            return self.json_response(404, {"error": "Not found."})
        if self.headers.get("Transfer-Encoding"):
            return self.json_response(400, {"error": "Transfer encoding is unsupported."})
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            return self.json_response(415, {"error": "Send application/json."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.json_response(400, {"error": "Invalid content length."})
        if not 0 < length <= MAX_BODY:
            return self.json_response(413, {"error": "Request size must be 1 to 12000 bytes."})
        try:
            raw = self.rfile.read(length)
            self._body_read = True
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")
            response = reply(data.get("message"))
        except RecursionError:
            return self.json_response(400, {"error": "JSON is nested too deeply."})
        except (ValueError, UnicodeDecodeError) as exc:
            return self.json_response(400, {"error": str(exc) if not isinstance(exc, json.JSONDecodeError) else "Invalid JSON."})
        except TimeoutError:
            return self.json_response(408, {"error": "Request timed out."})
        self.json_response(200, response)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(f"Medical information demo: http://127.0.0.1:{server.server_port}")
        print("Local use only. Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
