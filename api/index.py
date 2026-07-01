from http.server import BaseHTTPRequestHandler
import json
import time

# Global cache memory (ephemeral on Vercel, but matches user request)
active_users = {}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_POST(self):
        global active_users
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            laptop_name = data.get('laptopName')
            status = data.get('status')
            
            if laptop_name:
                if status == 'online':
                    active_users[laptop_name] = time.time()
                elif status == 'offline':
                    if laptop_name in active_users:
                        del active_users[laptop_name]
                        
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        import os
        if self.path == '/api' or self.path.startswith('/api?'):
            global active_users
            # Clean up stale users (e.g. haven't pinged in 6 minutes)
            current_time = time.time()
            timeout = 6 * 60 # 6 minutes (1 minute grace period over the 5 min ping)
            
            stale_users = [user for user, last_seen in active_users.items() if current_time - last_seen > timeout]
            for user in stale_users:
                del active_users[user]

            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "totalUsers": len(active_users),
                "users": list(active_users.keys())
            }
            self.wfile.write(json.dumps(response).encode())
            return

        # Serve static files for localhost testing
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if self.path == '/':
            filepath = os.path.join(base_dir, 'index.html')
            content_type = 'text/html'
        elif self.path == '/style.css':
            filepath = os.path.join(base_dir, 'style.css')
            content_type = 'text/css'
        elif self.path == '/script.js':
            filepath = os.path.join(base_dir, 'script.js')
            content_type = 'application/javascript'
        elif self.path == '/privacy.html':
            filepath = os.path.join(base_dir, 'privacy.html')
            content_type = 'text/html'
        elif self.path == '/rgb_wheel.ico' or self.path == '/favicon.ico':
            filepath = os.path.join(base_dir, 'rgb_wheel.ico')
            content_type = 'image/x-icon'
        else:
            self.send_response(404)
            self.end_headers()
            return
            
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(str(e).encode())

if __name__ == '__main__':
    from http.server import HTTPServer
    print("Starting local telemetry server on http://localhost:3000")
    server = HTTPServer(('localhost', 3000), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()
