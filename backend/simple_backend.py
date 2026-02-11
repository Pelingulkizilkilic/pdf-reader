from http.server import HTTPServer, BaseHTTPRequestHandler
import json

print("🚀 BACKEND BASLATILDI: http://localhost:5000")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status":"online","port":5000}')
    
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        if self.path == "/api/chat":
            response = {"answer": "Backend çalışıyor! Sorunuz alındı.", "success": True}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.wfile.write(b'{"status":"ok"}')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
