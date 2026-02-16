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
# Определяем путь к index.html относительно этого файла
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(CURRENT_DIR, 'index.html')

def get_local_ip():
    """Находит IP компьютера в локальной сети"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        s.close()
    except:
        IP = '127.0.0.1'
    return IP

class AppHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass 

    def do_GET(self):
        # 1. API для данных
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                resp = json.dumps(_LATEST_DATA, default=str, ensure_ascii=False)
            except Exception as e:
                resp = json.dumps({"error": str(e)})
            self.wfile.write(resp.encode('utf-8'))
            return

        # 2. Отдача HTML
        if self.path == '/' or self.path == '/index.html':
            if os.path.exists(TEMPLATE_PATH):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(TEMPLATE_PATH, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, f"File not found: {TEMPLATE_PATH}")
            return

def _server_thread():
    global _ACTUAL_PORT
    socketserver.TCPServer.allow_reuse_address = True
    
    attempt_port = PORT
    while True:
        try:
            with socketserver.TCPServer((HOST, attempt_port), AppHandler) as httpd:
                _ACTUAL_PORT = attempt_port
                print(f"\n🔭 DictScope LIVE:")
                print(f"   Local:   http://localhost:{attempt_port}")
                print(f"   Network: http://{get_local_ip()}:{attempt_port}\n")
                httpd.serve_forever()
            break
        except OSError as e:
            if e.errno == 98: # Address in use
                attempt_port += 1
            else:
                raise e

def render(data):
    """
    Запускает сервер (если еще не запущен) и обновляет данные.
    """
    global _LATEST_DATA, _SERVER_RUNNING
    _LATEST_DATA = data

    if not _SERVER_RUNNING:
        _SERVER_RUNNING = True
        t = threading.Thread(target=_server_thread, daemon=True)
        t.start()
        time.sleep(0.5)
        webbrowser.open(f"http://localhost:{_ACTUAL_PORT}")
