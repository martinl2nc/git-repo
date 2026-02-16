from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class MockN8NHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print("\n\n--- RECEIVED WEBHOOK DATA ---")
        print(f"Path: {self.path}")
        print(f"Headers: {self.headers}")
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            print("Payload JSON:")
            print(json.dumps(data, indent=2))
        except:
            print(f"Raw Body: {post_data.decode('utf-8')}")
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"message": "Mock received"}')

def run(server_class=HTTPServer, handler_class=MockN8NHandler, port=5678):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting mock n8n server on port {port}...")
    print("Press Ctrl+C to stop.")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
