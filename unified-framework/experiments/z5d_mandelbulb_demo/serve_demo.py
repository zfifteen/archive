#!/usr/bin/env python3
"""
Test HTML Demo Server
=====================

Simple HTTP server for testing the standalone HTML demo.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS headers."""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Simplified logging
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    # Change to the demo directory
    demo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(demo_dir)
    
    print("=" * 70)
    print("Z5D Mandelbulb Demo Server")
    print("=" * 70)
    print()
    print(f"Starting HTTP server on port {PORT}...")
    print(f"Serving from: {demo_dir}")
    print()
    print(f"Open your browser to:")
    print(f"  http://localhost:{PORT}/mandelbulb_demo.html")
    print()
    print("Controls:")
    print("  - Left mouse: Rotate camera")
    print("  - Scroll: Zoom in/out")
    print("  - P: Cycle Mandelbulb power")
    print("  - G: Toggle Z5D curvature")
    print("  - F: Toggle FPS counter")
    print("  - H: Hide UI")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Auto-open browser
    if '--no-browser' not in sys.argv:
        url = f'http://localhost:{PORT}/mandelbulb_demo.html'
        print(f"Opening browser to {url}...")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Could not open browser: {e}")
            print(f"Please manually open: {url}")
    
    # Start server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            httpd.shutdown()
            print("Server stopped.")


if __name__ == '__main__':
    main()
