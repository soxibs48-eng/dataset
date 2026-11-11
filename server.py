import http.server
import socketserver
import webbrowser
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print("=" * 60)
        print(f"🚀 SmartPrice AI Veb Sayti Ishga Tushdi!")
        print(f"Manzil: {url}")
        print("Saytni to'xtatish uchun: Ctrl + C bosing")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nVeb-server to'xtatildi.")

if __name__ == "__main__":
    main()

