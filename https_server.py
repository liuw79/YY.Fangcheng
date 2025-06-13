#!/usr/bin/env python3
import http.server
import socketserver
import ssl
import os
import threading
from datetime import datetime

HTTP_PORT = 8888
HTTPS_PORT = 443
DIRECTORY = '/var/www/fangcheng'
CERT_FILE = '/root/cert/gaowei.crt'
KEY_FILE = '/root/cert/gaowei.key'

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{"status": "healthy", "timestamp": "' + datetime.now().isoformat() + '", "protocol": "HTTPS"}'
            self.wfile.write(response.encode())
            return
        super().do_GET()

def start_http_redirect():
    """Start HTTP server (redirect to HTTPS)"""
    class HTTPSRedirectHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(301)
            host = self.headers.get("Host", "op.gaowei.com")
            if ":" in host:
                host = host.split(":")[0]
            self.send_header('Location', f'https://{host}{self.path}')
            self.end_headers()
    
    try:
        with socketserver.TCPServer(("0.0.0.0", HTTP_PORT), HTTPSRedirectHandler) as httpd:
            print(f"HTTP redirect server running on port {HTTP_PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"HTTP redirect server failed: {e}")

def start_https_main():
    """Start HTTPS server"""
    os.chdir(DIRECTORY)
    
    try:
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(CERT_FILE, KEY_FILE)
        
        with socketserver.TCPServer(("0.0.0.0", HTTPS_PORT), MyHTTPRequestHandler) as httpd:
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            print(f"HTTPS server running on port {HTTPS_PORT}")
            print(f"Access URL: https://op.gaowei.com")
            httpd.serve_forever()
    except Exception as e:
        print(f"HTTPS server failed: {e}")

if __name__ == "__main__":
    # Start HTTP redirect server (background thread)
    http_thread = threading.Thread(target=start_http_redirect, daemon=True)
    http_thread.start()
    
    # Start HTTPS server (main thread)
    start_https_main() 