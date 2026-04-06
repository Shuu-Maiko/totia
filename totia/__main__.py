import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

def _start_early_health_check():
    """Starts a minimal HTTP server instantly so Render doesn't time out while heavy ML libraries load."""
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args):
            pass 
            
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"[BOOT] Instantly mounted early health-check server on port {port}")

_start_early_health_check()

from .bot import TotiaBot

if __name__ == "__main__":
    bot = TotiaBot()
    bot.runBot()
