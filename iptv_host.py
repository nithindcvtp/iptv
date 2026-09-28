from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json, threading, webbrowser, os

BASE = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))
state = {"id": 0, "name": "", "url": ""}
DEFAULT_FILE = BASE / "iptv_default.json"
def get_default():
    try:
        d = json.loads(DEFAULT_FILE.read_text(encoding="utf-8"))
        if str(d.get("url","")).startswith(("http://","https://")): return d
    except Exception: pass
    return {"name":"","url":""}
lock = threading.Lock()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/default":
            raw = json.dumps(get_default()).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path == "/api/current":
            with lock: data = dict(state)
            raw = json.dumps(data).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path == "/":
            self.path = "/iptv_sender.html"
        elif path in ("/s1", "/s1/"):
            self.path = "/iptv_client.html"
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path != "/api/push":
            self.send_error(404); return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            name, url = str(body.get("name", ""))[:300], str(body.get("url", ""))[:5000]
            if not url.startswith(("http://", "https://")):
                self.send_error(400, "Invalid stream URL"); return
            with lock:
                state["id"] += 1; state["name"] = name; state["url"] = url
                result = dict(state)
            raw = json.dumps({"ok": True, "id": result["id"]}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        except Exception as e:
            self.send_error(400, str(e))

if __name__ == "__main__":
    os.chdir(BASE)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("S1 host running")
    print(f"Sender: http://localhost:{PORT}/")
    print(f"TV Client (S1): http://localhost:{PORT}/s1")
    print(f"Client: http://localhost:{PORT}/iptv_client.html")
    print("On another device, use this PC's LAN IP instead of localhost, e.g. http://192.168.1.10:8000/")
    print("Allow Python through Windows Firewall on Private networks if prompted.")
    if os.environ.get("OPEN_BROWSER", "1") == "1":
        threading.Timer(1, lambda: webbrowser.open(f"http://localhost:{PORT}/")).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("Stopping server…"); server.server_close()
