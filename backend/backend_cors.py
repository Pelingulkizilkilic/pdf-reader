from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

print("=" * 60)
print("🚀 BACKEND WITH FULL CORS")
print("📍 http://localhost:5000")
print("🔓 CORS: Tüm origin'lere açık")
print("=" * 60)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[{time.strftime('%H:%M:%S')}] GET {self.path}")
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/health':
            response = {
                'status': 'online',
                'port': 5000,
                'cors': 'enabled',
                'timestamp': time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.wfile.write(b'{"status":"ok"}')
    
    def do_POST(self):
        print(f"[{time.strftime('%H:%M:%S')}] POST {self.path}")
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print(f"Data: {post_data.decode()}")
        except:
            pass
        
        response = {'success': True, 'received': True}
        
        if self.path == '/api/upload':
            response.update({
                'id': f'pdf_{int(time.time())}',
                'filename': 'uploaded_file.pdf',
                'message': 'PDF başarıyla yüklendi'
            })
        elif self.path == '/api/chat':
            response.update({
                'answer': '✅ Backend çalışıyor! Sorunuz analiz edildi.',
                'source': 'Python Backend'
            })
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        print(f"[{time.strftime('%H:%M:%S')}] OPTIONS (CORS preflight)")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Default logları gizle

server = HTTPServer(('0.0.0.0', 5000), Handler)
print("✅ Backend hazır - CORS aktif")
server.serve_forever()
