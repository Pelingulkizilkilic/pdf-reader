import http.server
import socketserver

PORT = 8000

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok","port":8000}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

print(f"Starting simple backend on port {PORT}...")
with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
    print(f"Backend ready at http://localhost:{PORT}")
    httpd.serve_forever()
