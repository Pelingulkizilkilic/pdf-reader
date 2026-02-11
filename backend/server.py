from http.server import HTTPServer, BaseHTTPRequestHandler
import json

print("🚀 BACKEND BAŞLATILIYOR...")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b'{"status":"online"}')
    
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        if self.path == "/api/upload":
            self.wfile.write(b'{"id":"pdf_123","filename":"uploaded.pdf"}')
        elif self.path == "/api/chat":
            self.wfile.write(b'{"answer":"Backend cevap veriyor!"}')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

print("✅ http://localhost:8000")
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
