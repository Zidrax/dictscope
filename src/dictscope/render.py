import http.server
import socketserver
import threading
import json
import webbrowser
import time
import socket
import os
import sys

# --- CONFIG ---
PORT = 8000
HOST = ""  # 0.0.0.0 (доступно всем в сети)

_LATEST_DATA = {"status": "Waiting for data..."}
_SERVER_RUNNING = False
_ACTUAL_PORT = PORT

# --- PATH FINDER ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(CURRENT_DIR, "index.html")


def get_local_ip():
    """Находит IP компьютера в локальной сети"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
        s.close()
    except:
        IP = "127.0.0.1"
    return IP


def _pack(obj):
    """
    Превращает dict в структуру {"__map__": [[k, v], ...]},
    чтобы JSON не сортировал ключи, и JS сохранял порядок вставки.
    """
    if isinstance(obj, dict):
        # Превращаем словарь в список пар, рекурсивно обрабатывая значения
        return {"__map__": [[k, _pack(v)] for k, v in obj.items()]}
    elif isinstance(obj, (list, tuple)):
        return [_pack(x) for x in obj]
    else:
        return obj


class AppHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                packed_data = _pack(_LATEST_DATA)
                resp = json.dumps(packed_data, default=str, ensure_ascii=False)
            except Exception as e:
                resp = json.dumps({"error": str(e)})
            self.wfile.write(resp.encode("utf-8"))
            return

        if self.path == "/" or self.path == "/index.html":
            if os.path.exists(TEMPLATE_PATH):
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                with open(TEMPLATE_PATH, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, f"File not found: {TEMPLATE_PATH}")
            return


def _server_thread(quiet):
    global _ACTUAL_PORT
    socketserver.TCPServer.allow_reuse_address = True

    attempt_port = PORT
    while True:
        try:
            with socketserver.TCPServer((HOST, attempt_port), AppHandler) as httpd:
                _ACTUAL_PORT = attempt_port

                if not quiet:
                    print(f"\n🔭 DictScope LIVE:")
                    print(f"   Local:   http://localhost:{attempt_port}")
                    print(f"   Network: http://{get_local_ip()}:{attempt_port}\n")
                    print("")
                httpd.serve_forever()
            break
        except OSError as e:
            if e.errno == 98:  # Address in use
                attempt_port += 1
            else:
                raise e


def render(data, open_browser=False, quiet=False):
    """
    Update the DictScope viewer.

    :param data: Dictionary or list to visualize.
    :param open_browser: If True, opens web browser automatically.
    :param quiet: If True, suppresses console output.
    """
    global _LATEST_DATA, _SERVER_RUNNING
    _LATEST_DATA = data

    if not _SERVER_RUNNING:
        _SERVER_RUNNING = True
        t = threading.Thread(target=_server_thread, args=(quiet,), daemon=True)
        t.start()

        if open_browser:
            time.sleep(0.5)
            webbrowser.open(f"http://localhost:{_ACTUAL_PORT}")
