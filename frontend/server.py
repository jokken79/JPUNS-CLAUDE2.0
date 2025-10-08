#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend files
"""
import os
import http.server
import socketserver
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server(port=3000):
    """Run the HTTP server"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
        print(f"Servidor frontend corriendo en http://localhost:{port}")
        print(f"Abre http://localhost:{port}/templates/rirekisho.html en tu navegador")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()